"""Interface to the UTS (UMLS Terminology Services (UTS)) RESTful service,
which was taken from the UTS example repo.

:see `UTS GitHug repo <https://github.com/HHS/uts-rest-api/>`_

"""
__author__ = 'Paul Landes'

from typing import List, Dict, Any, Tuple, Union
from dataclasses import dataclass, field
import logging
import re
import json
from json.decoder import JSONDecodeError
import requests
from lxml.html import fromstring
from zensols.persist import Stash
from . import MedNLPError

logger = logging.getLogger(__name__)


class UTSError(MedNLPError):
    """An error thrown by wrapper of the UTS system."""
    pass


class NoResultsError(UTSError):
    """Thrown when no results, usually for a CUI not found."""
    pass


class AuthenticationError(UTSError):
    """Thrown when authentication fails."""
    def __init__(self, api_key: str):
        super().__init__(f'Authentication error using key: {api_key}')
        self.api_key = api_key


@dataclass
class Authentication(object):
    SERVICE = 'http://umlsks.nlm.nih.gov'
    """The service endpoint URL."""

    AUTH_URI = 'https://utslogin.nlm.nih.gov'
    """The authetication service endpoint URL."""

    api_key: str = field()
    """The API key used for the RESTful NIH service."""

    auth_endpoint: str = field(default='/cas/v1/api-key')
    """The path of the authentication service endpoint."""

    def gettgt(self):
        params = {'apikey': self.api_key}
        h = {'Content-type': 'application/x-www-form-urlencoded',
             'Accept': 'text/plain',
             'User-Agent': 'python'}
        r = requests.post(
            self.AUTH_URI + self.auth_endpoint, data=params, headers=h)
        if r.text[0] == '{':
            try:
                obj = json.loads(r.text)
                if 'authentication_exceptions' in obj:
                    raise AuthenticationError(self.api_key)
            except JSONDecodeError as e:
                logger.warning('looks like JSON, but not decodable: ' +
                               f'<{r.text}>: {e}')
        response = fromstring(r.text)
        # extract the entire URL needed from the HTML form (action attribute)
        # returned - looks similar to
        # https://utslogin.nlm.nih.gov/cas/v1/tickets/TGT-36471-aYqNLN2rFIJPXKzxwdTNC5ZT7z3B3cTAKfSc5ndHQcUxeaDOLN-cas
        # we make a POST call to this URL in the getst method
        tgt = response.xpath('//form/@action')[0]
        return tgt

    def getst(self, tgt):
        params = {'service': self.SERVICE}
        h = {'Content-type': 'application/x-www-form-urlencoded',
             'Accept': 'text/plain',
             'User-Agent': 'python'}
        r = requests.post(tgt, data=params, headers=h)
        st = r.text
        return st


@dataclass
class UTSClient(object):
    URI = 'https://uts-ws.nlm.nih.gov'
    """The service URL endpoint."""

    REL_ID_REGEX = re.compile(r'.*CUI\/(.+)$')
    """Used to parse related CUIs in :meth:`get_related_cuis`."""

    NO_RESULTS_ERR = 'No results containing all your search terms were found.'
    """Error message from UTS indicating a missing CUI."""

    MISSING_VALUE = '<missing>'
    """Value to store in the stash when there is a missing CUI."""

    api_key: str = field()
    """The API key used for the RESTful NIH service."""

    version: str = field(default='2020AA')
    """The version of the UML we want."""

    request_stash: Stash = field(default=None)

    def _get_ticket(self) -> str:
        """Generate a new service ticket for each page if needed."""
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'logging in to UTS with {self.api_key}')
        auth_client = Authentication(self.api_key)
        tgt = auth_client.gettgt()
        return auth_client.getst(tgt)

    def _parse_json(self, s: str) -> Union[Exception, Dict[str, Any]]:
        try:
            return json.loads(s)
        except JSONDecodeError as e:
            logger.debug(f'can not parse: <{s}>: {e}')
            return e

    def _request_remote(self, url: str, query: Dict[str, str],
                        expect: bool) -> Any:
        query['ticket'] = self._get_ticket()
        r = requests.get(url, params=query)
        r.encoding = 'utf-8'
        items = self._parse_json(r.text)
        if isinstance(items, Exception):
            raise UTSError(f'Could not parse: <{r.text}>, ' +
                           f'code: {r.status_code}') from items
        err = items.get('error')
        if err is not None and err == self.NO_RESULTS_ERR:
            if not expect:
                return None
            raise NoResultsError(
                f'Could not request {url}, query={query}: {err}')
        if r.status_code != 200:
            if err is None:
                msg = f'response: <{r.text}>'
            else:
                msg = err
            raise UTSError(f'Could not request {url}, query={query}: {msg}')
        if err is not None:
            raise UTSError(f'Could not request {url}, query={query}: {err}')
        if 'result' not in items:
            raise UTSError(f'Unknown resposne: <{r.text}>')
        return items['result']

    def _request_cache(self, url: str, query: Dict[str, str],
                       expect: bool) -> Any:
        q = '&'.join(map(lambda k: f'{k}={query[k]}', sorted(query.keys())))
        key = url + '?' + q
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'key: {key}')
        val = self.request_stash.load(key)
        if val is None:
            val = self._request_remote(url, query, expect)
            if val is None:
                val = self.MISSING_VALUE
            self.request_stash.dump(key, val)
        if val == self.MISSING_VALUE:
            val = None
        return val

    def _request(self, url: str, query: Dict[str, str], expect: bool) -> Any:
        if self.request_stash is None:
            return self._request_remote(url, query, expect)
        else:
            return self._request_cache(url, query, expect)

    def search_term(self, term: str, pages: int = 1) -> List[Dict[str, str]]:
        """Search for a string term in UMLS.

        :param term: the string term to match against

        :return: a list (one for each page), each with a dictionary of matching
                 terms that have the ``name`` of the term, the ``ui`` (CUI),
                 the ``uri`` of the term and the ``rootSource`` of the
                 orginitating system

        """
        url = '{uri}/rest/search/{version}'.format(
            **{'uri': self.URI, 'version': self.version})
        res = []
        for page_n in range(pages):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'fetching page {page_n}')
            query = {'string': term,
                     'page_n': page_n}
            res.extend(self._request(url, query, False)['results'])
        return res

    def get_atoms(self, cui: str, preferred: bool = True,
                  expect: bool = True) -> \
            Union[Dict[str, str], List[Dict[str, str]]]:
        """Get the UMLS atoms of a CUI from UTS.

        :param cui: the concept ID used to query

        :param preferred: if ``True`` only return preferred atoms

        :return: a list of atom entries in dictionary form or a single dict if
        `        ``preferred`` is ``True``

        """
        pat = '{uri}/rest/content/{version}/CUI/{cui}/atoms/'
        if preferred:
            pat += 'preferred/'
        url = pat.format(
            **{'uri': self.URI, 'version': self.version, 'cui': cui})
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'fetching atom {cui}')
        return self._request(url, {}, expect)

    def get_relations(self, cui: str, expect: bool = True) -> \
            List[Dict[str, Any]]:
        """Get the UMLS related concepts connected to a concept by ID.

        :param cui: the concept ID used to get related concepts

        :return: a list of relation entries in dictionary form in the order
                 returned by UTS

        """
        url = '{uri}/rest/content/{version}/CUI/{cui}/relations/'.format(
            **{'uri': self.URI, 'version': self.version, 'cui': cui})
        try:
            return self._request(url, {}, expect)
        except NoResultsError as e:
            if expect:
                raise e

    def get_related_cuis(self, cui: str, expect: bool = True) -> \
            List[Tuple[str, Dict[str, Any]]]:
        """Get the UMLS related concept IDs connected to a concept by ID.

        :param cui: the concept ID used to get related concepts

        :return: a list of tuples, each the related CUIs and the relation
                 entry, in the order returned by UTS

        """
        rel_ids = []
        relations = self.get_relations(cui, expect)
        if relations is None:
            if logger.isEnabledFor(logging.INFO):
                logger.info(f'no relations for cui {cui}')
        else:
            for rel in relations:
                rel_url = rel['relatedId']
                m = self.REL_ID_REGEX.match(rel_url)
                if m is None:
                    raise UTSError(
                        f'Could not parse relation ID from {rel_url}')
                rel_ids.append((m.group(1), rel))
        return rel_ids

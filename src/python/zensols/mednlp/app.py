"""A natural language medical domain parsing library.

"""
__author__ = 'Paul Landes'

from typing import Optional
from dataclasses import dataclass, field
from enum import Enum, auto
import sys
import logging
from io import TextIOBase
import re
from pprint import pprint
from pathlib import Path
import pandas as pd
from zensols.config import Dictable, ConfigFactory
from zensols.cli import ApplicationError
from zensols.nlp import FeatureDocumentParser, FeatureDocument
from zensols.nlp.dataframe import FeatureDataFrameFactory
from . import MedCatResource

logger = logging.getLogger(__name__)


class GroupInfo(Enum):
    """Used to group TUI information in :meth:`.Application.group`

    """
    csv = auto()
    byname = auto()


@dataclass
class Application(Dictable):
    """A natural language medical domain parsing library.

    """
    CLI_META = {'mnemonic_excludes': {'write'},
                'mnemonic_overrides': {'show_config': 'conf'},
                'option_excludes': {'doc_parser', 'config_factory'},
                'option_overrides': {'input_dir': {'long_name': 'input',
                                                   'short_name': 'i',
                                                   'metavar': 'DIR'}}}

    config_factory: ConfigFactory = field()
    """Used to create a cTAKES stash."""

    doc_parser: FeatureDocumentParser = field()
    """Parses and NER tags medical terms."""

    def _get_text(self, text_or_file: str) -> str:
        """Return the text from a file or the text passed based on if ``text_or_file``
        is a file on the file system.

        """
        path = Path(text_or_file)
        if path.is_file():
            with open(path) as f:
                text_or_file = f.read()
        return text_or_file

    def _write_doc(self, doc: FeatureDocument, only_medical: bool,
                   depth: int = 0, writer: TextIOBase = sys.stdout):
        for sent in doc.sents:
            if len(sent.text.strip()) == 0:
                continue
            self._write_line(sent.text, depth, writer)
            for tok in sent:
                if not only_medical or tok.is_ent:
                    self._write_line(f'{tok.norm}:', depth + 1, writer)
                    tok.write_attributes(depth + 2, writer, include_type=False)
            self._write_line('entities:', depth, writer)
            for ents in sent.entities:
                self._write_line(
                    ' '.join(map(lambda e: e.norm, ents)), depth + 1, writer)

    def show(self, text_or_file: str, only_medical: bool = False):
        """Parse and output medical entities.

        :param text_or_file: natural language to be processed

        :param only_medical: only provide medical linked tokens

        """
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'parsing: <{text_or_file}>...')
        text: str = self._get_text(text_or_file)
        doc: FeatureDocument = self.doc_parser.parse(text)
        self._write_doc(doc, only_medical)

    def _output_dataframe(self, df: pd.DataFrame, out: Optional[Path] = None):
        """Output the dataframe generated by other actions of the app.

        :param df: the dataframe to output:

        :param out: the output path, or ``None`` standard out
        """
        if out is None:
            out = sys.stdout
        df.to_csv(out, index=False)
        row_s = 's' if len(df) != 1 else ''
        if out != sys.stdout:
            logger.info(f'wrote {len(df)} row{row_s} to {out}')

    def features(self, text_or_file: str, out: Path = None, ids: str = None,
                 only_medical: bool = False):
        """Dump features as CSV output.

        :param text_or_file: natural language to be processed

        :param out: the path to output the CSV file or stdout if missing

        :param ids: the comma separate feature IDs to output

        :param only_medical: only provide medical linked tokens

        """
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'parsing: <{text_or_file}>...')
        params = {}
        if ids is None:
            ids = self.doc_parser.token_feature_ids
        else:
            ids = set(re.split(r'\W+', ids))
        needs = 'norm cui_ is_concept'.split()
        missing = set(filter(lambda i: i not in ids, needs))
        ids |= missing
        params['token_feature_ids'] = ids
        params['priority_feature_ids'] = needs
        df_fac = FeatureDataFrameFactory(**params)
        self.doc_parser.token_feature_ids = ids
        text: str = self._get_text(text_or_file)
        doc: FeatureDocument = self.doc_parser.parse(text)
        df: pd.DataFrame = df_fac(doc)
        if only_medical:
            df = df[df['is_concept'] == True]
        self._output_dataframe(df, out)

    def search(self, term: str):
        """Search the UMLS database using UTS and show results.

        :param term: the term to search for (eg 'lung cancer')

        """
        pprint(self.doc_parser.langres.uts_client.search_term(term))

    def atom(self, cui: str):
        """Search the UMLS database using UTS and show results.

        :param cui: the concept ID to search for (eg 'C0242379')

        """
        pprint(self.doc_parser.langres.uts_client.get_atoms(cui))

    def define(self, cui: str):
        """Look up an entity by CUI.  This takes a long time.

        :param cui: the concept ID to search for (eg 'C0242379')

        """
        entity = self.doc_parser.langres.get_linked_entity(cui)
        print(entity)

    def group(self, info: GroupInfo, query: str = None):
        """Get TUI group information.

        :param info: the type of information to return

        :param query: comma delimited name list used to subset the output data

        """
        res: MedCatResource = self.doc_parser.langres.medcat_resource
        df: pd.DataFrame = res.groups
        if info == GroupInfo.csv:
            path = Path('tui-groups.csv')
            df.to_csv(path)
            logger.info(f'wrote TUI groups to {path}')
        elif info == GroupInfo.byname:
            if query is None:
                raise ApplicationError('Missing query string for grouping')
            reg = '.*(' + '|'.join(query.split(',')) + ')'
            df = df[df['name'].str.match(reg)]
            print(','.join(df['tui'].tolist()))
        else:
            raise ApplicationError(f'Unkown query info type: {info}')

    def ctakes(self, text_or_file: str, only_medical: bool = False):
        """Invoke cTAKES on a directory with text files.

        :param text_or_file: natural language to be processed

        :param only_medical: only provide medical linked tokens

        """
        text: str = self._get_text(text_or_file)
        mc_res: MedCatResource = self.doc_parser.langres
        stash: CTakesParserStash = mc_res.get_new_ctakes_parser_stash()
        stash.set_documents([text])
        print(stash['0'].to_string())

    def similarity(self, term: str):
        """Get the cosine similarity between two CUIs.

        """
        for sim in self.doc_parser.langres.similarity_by_term(term):
            print(sim.cui)
            sim.write(1)

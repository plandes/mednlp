#!/usr/bin/env python

"""Demonstrates medical term feature generation from spaCy parsed natural
langauge.

This example needs the ``zensols.deepnlp`` library, install with::

    pip install zensols.deepnlp

"""
__author__ = 'Paul Landes'

from typing import Dict, List, Tuple
from dataclasses import dataclass, field
import logging
from gensim.models.keyedvectors import KeyedVectors
from zensols.cli import CliHarness
from zensols.cli import ProgramNameConfigurator
from zensols.mednlp import UTSClient
from zensols.mednlp.cui2vec import Cui2VecEmbedModel

logger = logging.getLogger(__name__)


# the definition of the application class executed from the CLI glue code
@dataclass
class Application(object):
    """Demonstrates access to UTS.

    """
    # tell the application not mistake the fields as an option when generating
    # the online help with the -h option
    CLI_META = {'option_excludes': {'uts_client', 'cui2vec_embedding'}}

    uts_client: UTSClient = field()
    """Queries UMLS data."""

    cui2vec_embedding: Cui2VecEmbedModel = field()
    """The cui2vec embedding model."""

    def similarity(self, term: str = 'heart disease', topn: int = 5):
        """Get the cosine similarity between two CUIs.

        :param term: the medical term

        :param topn: the top N count similarities to return

        """
        embedding: Cui2VecEmbedModel = self.cui2vec_embedding
        kv: KeyedVectors = embedding.keyed_vectors
        res: List[Dict[str, str]] = self.uts_client.search_term(term)
        cui: str = res[0]['ui']
        sims_by_word: List[Tuple[str, float]] = kv.similar_by_word(cui, topn)
        for rel_cui, proba in sims_by_word:
            rel_atom: Dict[str, str] = self.uts_client.get_atoms(rel_cui)
            rel_name = rel_atom.get('name', 'Unknown')
            print(f'{rel_name} ({rel_cui}): {proba * 100:.2f}%')


if (__name__ == '__main__'):
    CliHarness(
        app_config_resource='cui2vec.conf',
        app_config_context=ProgramNameConfigurator(
            None, default='cui2vec').create_section(),
        proto_args='',
        proto_factory_kwargs={'reload_pattern': '^cui2vec'},
    ).run()

#!/usr/bin/env python

"""Demonstrates medical term feature generation from spaCy parsed natural
langauge.

"""
__author__ = 'Paul Landes'

from dataclasses import dataclass, field
import itertools as it
import pandas as pd
from zensols.cli import CliHarness
from zensols.cli import ProgramNameConfigurator
from zensols.nlp import FeatureDocumentParser, FeatureDocument
from zensols.nlp.dataframe import FeatureDataFrameFactory

DEFAULT_SENT = 'He was diagnosed with kidney failure in the United States.'


# the definition of the application class executed from the CLI glue code
@dataclass
class Application(object):
    """Demonstrates access to UTS.

    """
    # tell the application not mistake the `doc_parser` as an option when
    # generating the online help with the -h option
    CLI_META = {'option_excludes': {'doc_parser'}}

    doc_parser: FeatureDocumentParser = field()
    """Parses and NER tags medical terms."""

    def _boundary(self, s: str):
        print(''.join(['-' * 5, s, '-' * 5]))

    def dump(self, sent: str):
        """Dump all features available to a CSV file."""
        doc: FeatureDocument = self.doc_parser(sent)
        df = pd.DataFrame(map(lambda t: t.asdict(), doc.tokens))
        df.to_csv('features.csv')

    def show(self, sent: str = None):
        """Parse a sentence and print all features for each token.

        :param sent: the sentence to parse and generate features

        """
        if sent is None:
            sent = DEFAULT_SENT

        self._boundary(f'sentence: <{sent}>')

        # parse the text in to a hierarchical langauge data structure
        doc: FeatureDocument = self.doc_parser(sent)
        print('first three tokens:')
        for tok in it.islice(doc.token_iter(), 3):
            print(tok.norm)
            tok.write_attributes(1, include_type=False)

        # named entities are also stored contiguous tokens at the document
        # level
        self._boundary('named entities:')
        for e in doc.entities:
            print(f'{e}: cui={e[0].cui_}')

        # generate a set of features from the document as a Pandas data frame
        # and print it
        feats = 'idx i norm is_concept cui_ pref_name_ ent_'.split()
        fac = FeatureDataFrameFactory(set(feats), feats)
        df: pd.DataFrame = fac(doc)
        self._boundary('features as a Pandas data frame')
        print(df)


if (__name__ == '__main__'):
    CliHarness(
        app_config_resource='features.conf',
        app_config_context=ProgramNameConfigurator(
            None, default='features').create_section(),
        proto_args=['dump', DEFAULT_SENT],
        proto_factory_kwargs={'reload_pattern': '^features'},
    ).run()

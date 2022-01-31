#!/usr/bin/env python

"""Demonstrates access to UMLS via CTAKES.

"""
__author__ = 'Paul Landes'

from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd
from zensols.cli import CliHarness, ProgramNameConfigurator
from zensols.mednlp.ctakes import CTakesParserStash


# the definition of the application class executed from the CLI glue code
@dataclass
class Application(object):
    """Demonstrates how to use the cTAKES application wrapper.

    """
    # tell the application not mistake the `uts_client` as an option when
    # generating the online help with the -h option
    CLI_META = {'option_excludes': {'uts_client'}}

    ctakes_stash: CTakesParserStash = field()
    """Runs the cTAKES CUI entity linker on a directory of medical notes."""

    def entities(self, sent: str = None, output: Path = None):
        """Parse a sentence and print cTAKES entities.

        :param sent: the sentence to parse and generate features

        """
        if sent is None:
            sent = 'He was diagnosed with kidney failure in the United States.'
        self.ctakes_stash.set_documents([sent])
        df: pd.DataFrame = self.ctakes_stash['0']
        print(df)
        if output is not None:
            df.to_csv(output)
            print(f'wrote: {output}')


if (__name__ == '__main__'):
    CliHarness(
        app_config_resource='ctakes.conf',
        app_config_context=ProgramNameConfigurator(
            None, default='ctakes').create_section(),
        proto_args='',
        proto_factory_kwargs={'reload_pattern': '^ctakes'},
    ).run()

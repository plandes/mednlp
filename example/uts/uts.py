#!/usr/bin/env python

"""Demonstrates access to UMLS via UTS.

"""
__author__ = 'Paul Landes'

from typing import Dict, List
from dataclasses import dataclass, field
from pprint import pprint
from zensols.cli import CliHarness, ProgramNameConfigurator
from zensols.mednlp import UTSClient


# the definition of the application class executed from the CLI glue code
@dataclass
class Application(object):
    """Demonstrates access to UTS.

    """
    # tell the application not mistake the `uts_client` as an option when
    # generating the online help with the -h option
    CLI_META = {'option_excludes': {'uts_client'}}

    uts_client: UTSClient = field()
    """Queries UMLS data."""

    def lookup(self, term: str = 'heart'):
        """Look up a term, then return the entry based on the CUI of the first found
        term.

        :param term: the term to search on

        """
        # terms are returned as a list of pages with dictionaries of data
        pages: List[Dict[str, str]] = self.uts_client.search_term(term)
        # get all term dictionaries from the first page
        terms: Dict[str, str] = pages[0]
        # get the concept unique identifier
        cui: str = terms['ui']

        # print atoms of this concept
        print('atoms:')
        pprint(self.uts_client.get_atoms(cui))

        # print all relationships from the concept to all others in the
        # ontology
        print('a few relations:')
        pprint(self.uts_client.get_relations(cui)[:2])


if (__name__ == '__main__'):
    CliHarness(
        app_config_resource='uts.conf',
        app_config_context=ProgramNameConfigurator(
            None, default='uts').create_section(),
        proto_args='',
    ).run()

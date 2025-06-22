"""Command line entry point to the application.

"""
__author__ = 'Paul Landes'

from typing import List, Any, Dict, Type
import sys
from zensols.cli import ApplicationFactory, ActionResult, CliHarness
from zensols.nlp import FeatureDocumentParser


class ApplicationFactory(ApplicationFactory):
    def __init__(self, *args, **kwargs):
        kwargs['package_resource'] = 'zensols.mednlp'
        super().__init__(*args, **kwargs)

    @classmethod
    def get_doc_parser(cls: Type) -> FeatureDocumentParser:
        """Get the default application's document parser."""
        return cls.create_harness().get_application().doc_parser


def main(args: List[str] = sys.argv, **kwargs: Dict[str, Any]) -> ActionResult:
    harness: CliHarness = ApplicationFactory.create_harness(relocate=False)
    harness.invoke(args, **kwargs)

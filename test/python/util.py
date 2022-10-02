import unittest
import sys
from zensols.cli import CliHarness
from zensols.persist import persisted
from zensols.mednlp import Application, ApplicationFactory


class TestBase(unittest.TestCase):
    def setUp(self):
        self.text = 'He was diagnosed with kidney failure and heart disease.'
        self.maxDiff = sys.maxsize

    @persisted('_app', cache_global=True)
    def _get_doc_parser(self):
        harness: CliHarness = ApplicationFactory.create_harness()
        app: Application = harness.get_instance(
            'show _ --config test-resources/mednlp-add-linker.conf --level=err')
        return app.doc_parser

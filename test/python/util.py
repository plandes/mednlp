import unittest
import sys
from zensols.cli import CliHarness, ApplicationFailure
from zensols.persist import persisted
from zensols.mednlp import Application, ApplicationFactory


class TestBase(unittest.TestCase):
    def setUp(self):
        import warnings
        warnings.simplefilter("ignore", ResourceWarning)
        self.text = 'He was diagnosed with kidney failure and heart disease.'
        self.maxDiff = sys.maxsize

    @persisted('_app', cache_global=True)
    def _get_doc_parser(self, config: str = 'mednlp'):
        harness: CliHarness = ApplicationFactory.create_harness()
        app: Application = harness.get_instance(
            f'show _ --config test-resources/{config}.conf --level=err')
        if isinstance(app, ApplicationFailure):
            raise app.exception
        return app.doc_parser

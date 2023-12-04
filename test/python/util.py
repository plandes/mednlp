import unittest
import sys
from zensols.cli import CliHarness, ApplicationFailure
from zensols.config import ConfigFactory
from zensols.mednlp import Application, ApplicationFactory


class TestBase(unittest.TestCase):
    def setUp(self):
        import warnings
        warnings.simplefilter("ignore", ResourceWarning)
        self.text = 'He was diagnosed with kidney failure and heart disease.'
        self.maxDiff = sys.maxsize

    def _get_doc_parser(self, config: str = 'mednlp', section: str = None):
        harness: CliHarness = ApplicationFactory.create_harness()
        args: str = f'--config test-resources/{config}.conf --level=err'
        if section is None:
            app: Application = harness.get_instance(f'show _ {args}')
            if isinstance(app, ApplicationFailure):
                raise app.exception
            return app.doc_parser
        else:
            harness: CliHarness = ApplicationFactory.create_harness()
            fac: ConfigFactory = harness.get_config_factory(args)
            return fac(section)

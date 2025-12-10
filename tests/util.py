import unittest
import sys
from zensols.cli import CliHarness, ApplicationFailure
from zensols.config import ConfigFactory
from zensols.nlp import FeatureDocumentParser
from zensols.mednlp import Application, ApplicationFactory, surpress_warnings


class TestBase(unittest.TestCase):
    def setUp(self):
        import warnings
        warnings.simplefilter("ignore", ResourceWarning)
        warnings.simplefilter("ignore", SyntaxWarning)
        surpress_warnings()
        self.text_1 = 'He was diagnosed with kidney failure and heart disease.'
        self.text_2 = 'He loved to smoke but Marlboro cigarettes gave John Smith lung cancer while he was in Chicago.'
        self.maxDiff = sys.maxsize

    def _get_doc_parser(self, config: str = 'default', section: str = None) -> \
            FeatureDocumentParser:
        harness: CliHarness = ApplicationFactory.create_harness()
        args: str = f'--config test-resources/config/{config}.conf --level=err'
        if section is None:
            app: Application = harness.get_instance(f'show _ {args}')
            if isinstance(app, ApplicationFailure):
                raise app.exception
            return app.doc_parser
        else:
            harness: CliHarness = ApplicationFactory.create_harness()
            fac: ConfigFactory = harness.get_config_factory(args)
            parser = fac(section)
            return parser

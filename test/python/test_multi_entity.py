import unittest
import sys
import json
from pathlib import Path
from zensols.cli import CliHarness
from zensols.persist import persisted
from zensols.nlp import FeatureDocument, FeatureDocumentParser
from zensols.mednlp import Application, ApplicationFactory


class TestMultiEntity(unittest.TestCase):
    @persisted('_app', cache_global=True)
    def _get_doc_parser(self):
        harness: CliHarness = ApplicationFactory.create_harness()
        app: Application = harness.get_instance(
            'show _ --config test-resources/mednlp-add-linker.conf --level=err')
        return app.doc_parser

    def setUp(self):
        self.text = 'He was diagnosed with kidney failure and heart disease.'
        self.maxDiff = sys.maxsize

    def test_multi_entity(self):
        sent = 'I love Chicago but Mike Ditka gives me lung cancer.'
        parser: FeatureDocumentParser = self._get_doc_parser()
        doc: FeatureDocument = parser.parse(sent)
        path = Path('test-resources/doc-features.json')
        json_str = doc.asjson(indent=4)
        obj = json.loads(json_str)
        for s in obj['sentences']:
            for t in s['tokens']:
                del t['context_similarity']
        # enable to re-write `should` test data for API changes; but have to
        # remove all `context_simirity` entries
        if 0:
            with open(path, 'w') as f:
                f.write(json_str)
        with open(path) as f:
            should = json.load(f)
        self.assertEqual(should, obj)

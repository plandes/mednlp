import json
from pathlib import Path
from zensols.nlp import FeatureDocument, FeatureDocumentParser
from util import TestBase


class TestMultiEntity(TestBase):
    def test_multi_entity(self):
        sent = 'I love Chicago but Mike Ditka gives me lung cancer.'
        parser: FeatureDocumentParser = self._get_doc_parser('mednlp-add-linker')
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

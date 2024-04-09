import json
import re
from pathlib import Path
from zensols.nlp import FeatureDocument, FeatureDocumentParser, FeatureToken
from util import TestBase


class TestMultiEntity(TestBase):
    def test_multi_entity(self):
        def filter_json_line(s: str) -> bool:
            return re.match(r'^\s*"context_similarity":\s*-?1,?\s*$', s) is None

        DEBUG: bool = False
        WRITE: bool = False
        sent = 'John was diagnosed with kidney failure. He has lung cancer too.'
        parser: FeatureDocumentParser = \
            self._get_doc_parser('mednlp-add-linker')
        doc: FeatureDocument = parser.parse(sent)
        if DEBUG:
            tok: FeatureToken
            for tok in doc.token_iter():
                print(tok, tok.definition_)
                tok.write()
        path = Path('test-resources/entlink-features.json')
        json_str = doc.asjson(indent=4)
        obj = json.loads(json_str)
        for s in obj['sentences']:
            for t in s['tokens']:
                del t['context_similarity']
        if WRITE:
            with open(path, 'w') as f:
                line: str
                # enable to re-write `should` test data for API changes; but
                # have to remove all `context_simirity` entries
                for line in filter(filter_json_line, json_str.split('\n')):
                    f.write(line + '\n')
        with open(path) as f:
            should = json.load(f)
        self.assertEqual(should, obj)

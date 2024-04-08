from typing import Dict
import json
from pathlib import Path
from zensols.nlp import (
    FeatureToken, FeatureSentence, FeatureDocument, FeatureDocumentParser
)
from util import TestBase


class TestParse(TestBase):
    def test_feature_parse(self):
        DEBUG: bool = False
        keeps = set('cui_ pref_name_'.split())
        parser: FeatureDocumentParser = self._get_doc_parser()
        self.assertTrue(isinstance(parser, FeatureDocumentParser))
        med_toks: Dict[str, str] = []
        doc: FeatureDocument = parser(self.text_1)
        for tok in doc.token_iter():
            fd = tok.asdict()
            med_toks.append({k: fd[k] for k in fd.keys() & keeps})
        if DEBUG:
            print()
            for tok in doc.token_iter():
                print(tok, tok.cui_, tok.pref_name_)
            print()
            for tok in med_toks:
                print(tok)
        none = FeatureToken.NONE
        for i, mtok in enumerate(med_toks):
            if DEBUG:
                print(i, mtok)
            if i >= 4 and i <= 5:
                self.assertEqual(
                    {'cui_': 'C0035078', 'pref_name_': 'Kidney Failure'}, mtok)
            else:
                self.assertEqual({'cui_': none, 'pref_name_': none}, mtok)

    def test_doc_parse(self):
        parser: FeatureDocumentParser = self._get_doc_parser()
        self.assertTrue(isinstance(parser, FeatureDocumentParser))
        doc: FeatureDocument = parser.parse(self.text_1)
        self.assertTrue(isinstance(doc, FeatureDocument))
        sent: FeatureSentence = doc[0]
        self.assertTrue(isinstance(sent, FeatureSentence))
        self.assertEqual(10, len(sent))
        self.assertTrue(isinstance(sent[0], FeatureToken))
        self.assertTrue('C0011900', sent[2].cui_)
        self.assertTrue('Diagnosis', sent[2].pref_name_)
        self.assertTrue('C0035078', sent[4].cui_)
        self.assertTrue('Kidney Failure', sent[4].pref_name_)

    def test_multi_entity(self):
        WRITE: bool = False
        parser: FeatureDocumentParser = self._get_doc_parser()
        doc: FeatureDocument = parser.parse(self.text_2)
        path = Path('test-resources/doc-features.json')
        json_str = doc.asjson(indent=4)
        obj = json.loads(json_str)
        for s in obj['sentences']:
            for t in s['tokens']:
                del t['context_similarity']
        # enable to re-write `should` test data for API changes; but have to
        # remove all `context_simirity` entries
        if WRITE:
            with open(path, 'w') as f:
                json.dump(obj, f, indent=4)
        with open(path) as f:
            should = json.load(f)
        self.assertEqual(should, obj)

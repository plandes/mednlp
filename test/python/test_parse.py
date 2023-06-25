import json
from pathlib import Path
from zensols.nlp import (
    FeatureToken, FeatureSentence, FeatureDocument, FeatureDocumentParser
)
from util import TestBase


class TestParse(TestBase):
    def test_feature_parse(self):
        keeps = set('cui_ pref_name_'.split())
        parser: FeatureDocumentParser = self._get_doc_parser()
        self.assertTrue(isinstance(parser, FeatureDocumentParser))
        med_toks = []
        for tok in parser(self.text).token_iter():
            fd = tok.asdict()
            med_toks.append({k: fd[k] for k in fd.keys() & keeps})
        none = FeatureToken.NONE
        self.assertEqual({'cui_': none, 'pref_name_': none},
                         med_toks[0])
        self.assertEqual({'cui_': 'C0011900', 'pref_name_': 'Diagnosis'},
                         med_toks[2])
        self.assertEqual({'cui_': 'C0035078', 'pref_name_': 'Kidney Failure'},
                         med_toks[4])

    def test_doc_parse(self):
        parser: FeatureDocumentParser = self._get_doc_parser()
        self.assertTrue(isinstance(parser, FeatureDocumentParser))
        doc: FeatureDocument = parser.parse(self.text)
        self.assertTrue(isinstance(doc, FeatureDocument))
        sent: FeatureSentence = doc[0]
        self.assertTrue(isinstance(sent, FeatureSentence))
        self.assertEqual(10, len(sent))
        self.assertTrue(isinstance(sent[0], FeatureToken))
        self.assertTrue('C0011900', sent[2].cui_)
        self.assertTrue('Diagnosis', sent[2].pref_name_)
        self.assertTrue('C0035078', sent[4].cui_)
        self.assertTrue('Kidney Failure', sent[4].pref_name_)

    def _test_multi_entity(self):
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

import logging
import unittest
import sys
import json
from spacy.tokens.doc import Doc
from pathlib import Path
from zensols.cli import CliHarness
from zensols.nlp import (
    TokenFeatures, FeatureToken,
    FeatureSentence, FeatureDocument, FeatureDocumentParser
)
from zensols.mednlp import Application, ApplicationFactory


if 0:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)


class TestApp(unittest.TestCase):
    def setUp(self):
        harness: CliHarness = ApplicationFactory.create_harness()
        self.app = harness.get_instance(
            'show _ --config test-resources/mednlp.conf --level=err')
        self.text = 'He was diagnosed with kidney failure and heart disease.'
        self.maxDiff = sys.maxsize

    def test_feature_parse(self):
        keeps = set('cui_ pref_name_'.split())
        app: Application = self.app
        parser: FeatureDocumentParser = app.doc_parser
        self.assertTrue(isinstance(parser, FeatureDocumentParser))
        doc: Doc = parser.langres.parse(self.text)
        self.assertTrue(Doc, type(doc))
        med_feats = []
        for feat in parser.langres.features(doc):
            fd = feat.asdict()
            med_feats.append({k: fd[k] for k in fd.keys() & keeps})
        none = TokenFeatures.NONE
        self.assertEqual({'cui_': none, 'pref_name_': none},
                         med_feats[0])
        self.assertEqual({'cui_': 'C0011900', 'pref_name_': 'Diagnosis'},
                         med_feats[2])
        self.assertEqual({'cui_': 'C0035078', 'pref_name_': 'Kidney Failure'},
                         med_feats[4])

    def test_doc_parse(self):
        app = self.app
        parser: FeatureDocumentParser = app.doc_parser
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

    def test_multi_entity(self):
        sent = 'I love Chicago but Mike Ditka gives me lung cancer.'
        app = self.app
        parser: FeatureDocumentParser = app.doc_parser
        doc: FeatureDocument = parser.parse(sent)
        path = Path('test-resources/doc-features.json')
        json_str = doc.asjson(indent=4)
        obj = json.loads(json_str)
        for s in obj['sentences']:
            for t in s['tokens']:
                del t['context_similarity']
        # enable to re-write `should` test data for API changes
        if 0:
            with open(path, 'w') as f:
                f.write(json_str)
        with open(path) as f:
            should = json.load(f)
        self.assertEqual(should, obj)

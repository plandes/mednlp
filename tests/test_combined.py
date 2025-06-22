from typing import List, Dict, Set, Any
from collections import OrderedDict
import json
from zensols.nlp import FeatureToken, FeatureDocument, FeatureDocumentParser
from util import TestBase


class TestCombinedParsers(TestBase):
    _DEFAULT_ATTRS = 'i i_sent idx norm ent_ ent_iob ent_iob_'.split()
    _TRACE = False

    def _compare_sents(self, parser_name: str, idx: int, write: bool,
                       sent: str, attrs: List[str], missing: Set[str],
                       config: str = 'combined'):
        def map_tok_features(t: FeatureToken) -> Dict[str, Any]:
            # sort keys to make diffing easier
            dct = t.asdict()
            return OrderedDict(sorted(dct.items(), key=lambda t: t[0]))

        actual_file: str = f'test-resources/should/{parser_name}-{idx}.json'
        p: FeatureDocumentParser = self._get_doc_parser(config, parser_name)
        doc: FeatureDocument = p(sent)

        actuals = tuple(map(map_tok_features, doc.token_iter()))
        if self._TRACE:
            from pprint import pprint
            pprint(actuals)
            return
        if write:
            print(sent)
            with open(actual_file, 'w') as f:
                json.dump(actuals, f, indent=4, sort_keys=False)
            for attr in attrs:
                vals: str = ', '.join(map(lambda d: str(d[attr]), actuals))
                print(f'  {attr}: {vals}')
            print('_' * 79)

        with open(actual_file) as f:
            shoulds: List[Dict[str, Any]] = json.load(f)

        attr: str
        for attr in attrs:
            actual = tuple(map(lambda d: d[attr], actuals))
            should = tuple(map(lambda d: d[attr], shoulds))
            self.assertEqual(should, actual, f'for attribute: <{attr}>')

        if missing is not None:
            for attr in missing:
                for tok in actuals:
                    self.assertFalse(hasattr(tok, attr),
                                     f'expected missing {attr} in {tok}')

    def _compare(self, parser_name: str, write: bool = False,
                 attrs: List[str] = None, missing: Set[str] = None):
        attrs = TestCombinedParsers._DEFAULT_ATTRS if attrs is None else attrs
        for i in range(2):
            sent: str = getattr(self, f'text_{i + 1}')
            self._compare_sents(parser_name, i, write, sent, attrs, missing)

    def test_default(self):
        self._compare('doc_parser', missing='cui_'.split())

    def test_biomed_ner(self):
        self._compare('mednlp_biomed_doc_parser', missing='cui_'.split())

    def test_medcat(self):
        self._compare('mednlp_medcat_doc_parser',
                      attrs=self._DEFAULT_ATTRS + 'cui_ tuis_'.split())

    def test_biomed_combined(self):
        self._compare('mednlp_combine_biomed_doc_parser',
                      missing='cui_'.split())

    def test_medcat_combined(self):
        self._compare('mednlp_combine_medcat_doc_parser',
                      attrs=self._DEFAULT_ATTRS + 'cui_ tuis_'.split())

    def test_medcat_biomded_combined(self):
        self._compare('mednlp_combine_biomed_medcat_doc_parser',
                      attrs=self._DEFAULT_ATTRS + 'cui_ tuis_'.split())

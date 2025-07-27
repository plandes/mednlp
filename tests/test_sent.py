from util import TestBase
from io import StringIO
from pathlib import Path
from zensols.nlp import FeatureDocument, FeatureDocumentParser


class TestSentenceChunking(TestBase):
    WRITE: bool = False

    def _run_compare(self, config: str):
        should = Path(f'test-resources/sent/{config}.txt')
        input_str = "The patient was admitted on 03/26/08\n and was started on IV antibiotics elevation" +\
            ", was also counseled to minimizing the cigarette smoking. The patient had edema\n\n" +\
            "\n of his bilateral lower extremities. The hospital consult was also obtained to " +\
            "address edema issue question was related to his liver hepatitis C. Hospital consult" +\
            " was obtained. This included an ultrasound of his abdomen, which showed just mild " +\
            "cirrhosis. "
        parser: FeatureDocumentParser = self._get_doc_parser(config)
        self.assertTrue(isinstance(parser, FeatureDocumentParser))
        doc: FeatureDocument = parser(input_str)
        sio = StringIO()
        for sent in doc.sents:
            sio.write(f'<{sent.text}>\n')
        if self.WRITE:
            should.write_text(sio.getvalue())
        self.assertEqual(should.read_text(), sio.getvalue())

    def test_default(self):
        self._run_compare('default')

    def test_rush(self):
        self._run_compare('pyrush')

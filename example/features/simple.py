#!/usr/bin/env python

from zensols.nlp import FeatureDocument, FeatureDocumentParser
from zensols.mednlp import ApplicationFactory


def main():
    doc_parser: FeatureDocumentParser = ApplicationFactory.get_doc_parser()
    doc: FeatureDocument = doc_parser('John was diagnosed with kidney failure')
    for tok in doc.tokens:
        print(tok.norm, tok.pos_, tok.tag_, tok.cui_, tok.detected_name_)
    print(doc.entities)


if (__name__ == '__main__'):
    main()

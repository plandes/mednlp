"""A vectorizer for the ``en_ner_bionlp13cg_md`` SciSpacy model. See the
``resources/bioner.yml`` resource library.

"""
__author__ = 'Paul Landes'

from typing import ClassVar
from dataclasses import dataclass
from zensols.deepnlp.vectorize import SpacyFeatureVectorizer


@dataclass
class BionlpSpacyFeatureVectorizer(SpacyFeatureVectorizer):
    """A named entity recoginizer for the SciSpacy ``en_ner_bionlp13cg_md``
    model.  Before use, this class needs to be registered with the
    :meth:`~zensols.deepnlp.vectorize.spacy.SpacyFeatureVectorizer.register`
    method.

    :see: :class:`~zensols.deepnlp.vectorize.spacy.NamedEntityRecognitionFeatureVectorizer`

    """
    DESCRIPTION: ClassVar[str] = 'medical named entity recognition'
    LANG: ClassVar[str] = 'en'
    FEATURE_ID: ClassVar[str] = 'medent'
    SYMBOLS: ClassVar[str] = """AMINO_ACID ANATOMICAL_SYSTEM CANCER CELL
CELLULAR_COMPONENT DEVELOPING_ANATOMICAL_STRUCTURE GENE_OR_GENE_PRODUCT
IMMATERIAL_ANATOMICAL_ENTITY MULTI-TISSUE_STRUCTURE ORGAN ORGANISM
ORGANISM_SUBDIVISION ORGANISM_SUBSTANCE PATHOLOGICAL_FORMATION SIMPLE_CHEMICAL
TISSUE"""

from __future__ import annotations
"""Medical langauge parser.

"""
__author__ = 'Paul Landes'

from typing import Type, Iterable, Dict, Tuple, Set
from dataclasses import dataclass, field
import logging
import collections
from spacy.tokens.token import Token
from spacy.tokens.doc import Doc
from spacy.language import Language
from scispacy.linking_utils import Entity as SciSpacyEntity
from zensols.nlp import (
    FeatureToken, SpacyFeatureDocumentParser, FeatureDocumentParser
)
from . import MedNLPError, MedCatResource, MedicalFeatureToken
from .domain import _MedicalEntity

logger = logging.getLogger(__name__)


@dataclass
class MedicalFeatureDocumentParser(SpacyFeatureDocumentParser):
    """A medical based language resources that parses concepts.

    """
    TOKEN_FEATURE_IDS = frozenset(FeatureDocumentParser.TOKEN_FEATURE_IDS |
                                  MedicalFeatureToken.FEATURE_IDS)
    """Default token feature ID set for the medical parser.

    """
    token_feature_ids: Set[str] = field(default=TOKEN_FEATURE_IDS)
    """The features to keep from spaCy tokens.

    :see: :obj:`TOKEN_FEATURE_IDS`

    """
    token_class: Type[FeatureToken] = field(default=MedicalFeatureToken)
    """The class to use for instances created by :meth:`features`."""

    medcat_resource: MedCatResource = field(default=None)
    """The MedCAT factory resource."""

    include_definition: bool = field(default=False)
    """If ``True``, include the concept definition in token features."""

    def __post_init__(self):
        if self.medcat_resource is None:
            raise MedNLPError('No medcat resource set')
        super().__post_init__()

    def _create_model_key(self) -> str:
        return f'name-{self.name}'

    def _create_model(self) -> Language:
        return self.medcat_resource.cat.get_spacy_nlp()

    def _create_token(self, tok: Token, norm: Tuple[Token, str],
                      *args, **kwargs) -> FeatureToken:
        tp: Type[FeatureToken] = self.token_class
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'create token: {tok}/{norm}')
            logger.debug(f'args: <{args}>')
            logger.debug(f'kwargs: <{kwargs}>')
        f: FeatureToken = tp(tok, norm, *args, **kwargs)
        if self.include_definition and f.is_concept:
            e: SciSpacyEntity = self.get_linked_entity(f.cui_)
            if e is not None:
                f._definition = e.definition
        return f.detach(self.token_feature_ids)

    def _normalize_tokens(self, doc: Doc) -> Iterable[FeatureToken]:
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'parsing: {doc}')

        # load/create model resources
        res: MedCatResource = self.medcat_resource
        ix2ent: Dict[int, _MedicalEntity] = collections.defaultdict(_MedicalEntity)

        # add entities
        for ent in doc.ents:
            for i in range(ent.start, ent.end):
                tok = doc[i]
                ix2ent[tok.idx].concept_span = ent

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'normalizing with: {self.token_normalizer}')

        return super()._normalize_tokens(doc, res=res, ix2ent=ix2ent)

from __future__ import annotations
"""Contains the classes for the medical token type.

"""
__author__ = 'Paul Landes'

from typing import Union, Dict, Optional, Tuple
import logging
from functools import reduce
from frozendict import frozendict
from spacy.tokens.token import Token
from spacy.tokens.span import Span
from medcat.cdb import CDB
from zensols.nlp import FeatureToken, SpacyFeatureToken
from . import MedCatResource
from .domain import _MedicalEntity

logger = logging.getLogger(__name__)


class MedicalFeatureToken(SpacyFeatureToken):
    """A set of token features that optionally contains a medical concept.

    """
    FEATURE_IDS_BY_TYPE = frozendict({
        'str': frozenset(('cui_ pref_name_ detected_name_ tuis_ ' +
                          'definition_ tui_descs_').split()),
        'bool': frozenset('is_concept'.split()),
        'float': frozenset('context_similarity'.split()),
        'int': frozenset('cui'.split()),
        'list': frozenset('tuis sub_names'.split())})
    FEATURE_IDS = frozenset(
        reduce(lambda res, x: res | x, FEATURE_IDS_BY_TYPE.values()))
    WRITABLE_FEATURE_IDS = tuple(list(FeatureToken.WRITABLE_FEATURE_IDS) +
                                 'cui_'.split())
    CONCEPT_ENTITY_LABEL = 'concept'
    _NONE_SET = frozenset()

    def __init__(self, spacy_token: Union[Token, Span], norm: str,
                 res: MedCatResource, ix2ent: Dict[int, _MedicalEntity]):
        super().__init__(spacy_token, norm)
        self._definition: str = self.NONE
        self._cdb: CDB = res.cat.cdb
        self._res = res
        med_ent: Optional[_MedicalEntity] = ix2ent.get(self.idx)
        if med_ent is None:
            med_ent = _MedicalEntity()
        self.med_ent = med_ent
        self.is_ent = med_ent.is_ent

    @property
    def ent(self) -> str:
        return self.med_ent.concept_span.label if self.is_concept else super().ent

    @property
    def ent_(self) -> str:
        return self.med_ent.concept_span.label_ if self.is_concept else super().ent_

    @property
    def is_concept(self) -> bool:
        """``True`` if this has a CUI and identifies a medical concept."""
        return self.is_ent

    @property
    def cui_(self) -> str:
        """The unique UMLS concept ID."""
        return self.med_ent.cui_ if self.is_concept else self.NONE

    @property
    def cui(self) -> int:
        """Returns the numeric part of the concept ID."""
        return -1 if not self.is_concept else int(self.cui_[1:])

    @property
    def pref_name_(self) -> str:
        """The preferred name of the concept."""
        if self.is_concept:
            return self._cdb.cui2preferred_name.get(self.cui_)
        else:
            return self.NONE

    @property
    def detected_name_(self) -> str:
        """The detected name of the concept."""
        if self.is_concept:
            return self.med_ent.concept_span._.detected_name
        else:
            return self.NONE

    @property
    def sub_names(self) -> Tuple[str]:
        """Return other names for the concept."""
        if self.is_concept:
            return tuple(sorted(self._cdb.cui2names[self.cui_]))
        else:
            return []

    @property
    def context_similarity(self) -> float:
        """The similiarity of the concept."""
        if self.is_concept:
            return self.med_ent.concept_span._.context_similarity
        else:
            return -1

    @property
    def definition_(self) -> str:
        """The definition if the concept."""
        return self._definition or FeatureToken.NONE

    @property
    def tuis(self) -> Tuple[str]:
        """The the CUI type of the concept."""
        if self.is_concept:
            cui: str = self.cui_
            return tuple(sorted(self._cdb.cui2type_ids.get(cui)))
        else:
            return self._NONE_SET

    @property
    def tuis_(self) -> str:
        """All CUI TUIs (types) of the concept sorted as a comma delimited list.

        """
        return ','.join(sorted(self.tuis))

    @property
    def tui_descs_(self) -> str:
        """Descriptions of :obj:`tuis_`."""
        def map_tui(k: str) -> str:
            v = self._res.tuis.get(k)
            if v is None:
                v = f'? ({k})'
            return v

        return ', '.join(map(map_tui, sorted(self.tuis)))

    def __str__(self):
        cui_str = f' ({self.cui_})' if self.is_concept else ''
        return self.norm + cui_str

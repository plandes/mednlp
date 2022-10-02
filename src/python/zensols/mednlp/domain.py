from __future__ import annotations
"""Contains the classes for the medical token type and others.

"""
__author__ = 'Paul Landes'

from typing import Optional
from dataclasses import dataclass, field
import logging
from spacy.tokens.span import Span
from zensols.util import APIError
from zensols.config import Dictable

logger = logging.getLogger(__name__)


class MedNLPError(APIError):
    """Raised by any medical NLP speicic reason in this library."""
    pass


@dataclass
class _MedicalEntity(object):
    """Container class for general and medical specific named entities.  Instances
    of this class have the NER from a vanilla spaCy model output and the NER+L
    linked UMLS concepts.

    """
    concept_span: Optional[Span] = field(default=None)
    """The UMLS concept medical domain entity."""

    @property
    def is_concept(self) -> bool:
        return self.concept_span is not None

    @property
    def is_ent(self) -> bool:
        return self.concept_span is not None

    @property
    def cui(self) -> str:
        return int(self.cui_[1:])

    @property
    def cui_(self) -> str:
        return self.concept_span._.cui

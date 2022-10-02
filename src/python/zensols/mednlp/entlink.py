from __future__ import annotations
"""Contains the classes for the medical token type and others.

"""
__author__ = 'Paul Landes'

from typing import Optional
from dataclasses import dataclass, field, InitVar
import logging
from spacy.tokens.span import Span
from scispacy.linking import EntityLinker
from scispacy.linking_utils import Entity as SciSpacyEntity
from zensols.util import APIError
from zensols.persist import persisted, PersistedWork
from zensols.config import Dictable
from zensols.nlp import SpacyFeatureTokenDecorator

logger = logging.getLogger(__name__)


@dataclass
class Entity(Dictable):
    """A convenience container class that Wraps a SciSpacy entity.

    """
    _DICTABLE_ATTRIBUTES = 'cui name definition'.split()

    sci_spacy_entity: SciSpacyEntity = field(repr=False)
    """The entity identified by :mod:`scispacy.linking_utils`."""

    @property
    def name(self) -> str:
        """The canonical name of the entity."""
        return self.sci_spacy_entity.canonical_name

    @property
    def definition(self) -> str:
        """The human readable description of the entity."""
        return self.sci_spacy_entity.definition

    @property
    def cui(self) -> str:
        """The unique concept identifier."""
        return self.sci_spacy_entity.concept_id

    def __str__(self) -> str:
        return f'{self.name} ({self.cui})'

    def __repr__(self):
        return self.cui


@dataclass
class EntitySimilarity(Entity):
    """A similarity measure of a medical concept in cui2vec.

    :see: :meth:`.MedicalFeatureDocumentParser.similarity_by_term`
    """
    similiarty: float = field()


@dataclass
class EntityLinkerResource(object):
    """Provides a way resolve :class:`scispacy.linking_utils.Entity` instances from
    CUIs.

    :see: :meth:`.get_linked_entity`

    """
    params: Dict[str, Any] = field(
        default_factory=lambda: {'resolve_abbreviations': True,
                                 'linker_name': 'umls'})
    """Parameters given to the scispaCy entity linker."""

    cache_global: InitVar[bool] = field(default=True)
    """Whether or not to globally cache resources, which saves load time.

    """
    def __post_init__(self, cache_global: bool):
        self._linker = PersistedWork(
            '_linker', self, cache_global=cache_global)

    @property
    @persisted('_linker')
    def linker(self) -> EntityLinker:
        """The ScispaCy entity linker."""
        self._silence_scispacy_warn()
        return EntityLinker(**self.params)

    @staticmethod
    def _silence_scispacy_warn():
        """This warning has should have no bearing on this application as we're simply
        doing a CUI looking.

        """
        import warnings
        s = '.*Trying to unpickle estimator Tfidf(?:Transformer|Vectorizer) from version.*'
        warnings.filterwarnings('ignore', message=s)
        s = 'Please use `csr_matrix` from the `scipy.sparse` namespace.*'
        warnings.filterwarnings('ignore', message=s)

    def get_linked_entity(self, cui: str) -> Entity:
        """Get a scispaCy linked entity.

        :param cui: the unique concept ID

        """
        linker: EntityLinker = self.linker
        se: SciSpacyEntity = linker.kb.cui_to_entity.get(cui)
        if se is not None:
            return Entity(se)


@dataclass
class LinkFeatureTokenDecorator(SpacyFeatureTokenDecorator):
    """Adds linked SciSpacy definitions to tokens using the
    :class:`.MedicalLibrary`.

    """
    lib: MedicalLibrary = field(default=None)
    """The medical library used for linking entities."""

    def decorate(self, spacy_tok: Token, feature_token: FeatureToken):
        e: SciSpacyEntity = self.lib.get_linked_entity(feature_token.cui_)
        if e is not None:
            feature_token._definition = e.definition

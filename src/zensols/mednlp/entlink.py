"""Contains the classes for the medical token type and others.

"""
__author__ = 'Paul Landes'

from typing import Tuple, Dict, Any
from dataclasses import dataclass, field, InitVar
import logging
from scispacy.linking import EntityLinker
from scispacy.linking_utils import Entity as SciSpacyEntity
from zensols.persist import persisted, PersistedWork
from zensols.config import Dictable
from zensols.nlp import FeatureToken, FeatureTokenDecorator
from . import MedicalLibrary

logger = logging.getLogger(__name__)


@dataclass
class Entity(Dictable):
    """A UMLS entity that has its name, CUI, definition and aliases.

    """
    name: str = field()
    """The canonical name of the entity."""

    cui: str = field()
    """The unique concept identifier."""

    definition: str = field()
    """The human readable description of the entity."""

    aliases: Tuple[str, ...] = field()
    """Aliases for the term."""

    tuis: Tuple[str, ...] = field()
    """Type union IDs."""

    def __str__(self) -> str:
        return f'{self.name} ({self.cui})'

    def __repr__(self):
        return self.cui


@dataclass
class EntitySimilarity(Entity):
    """A similarity measure of a medical concept in cui2vec.

    :see: :meth:`.MedCatFeatureDocumentParser.similarity_by_term`

    """
    similiarty: float = field()


@dataclass
class EntityLinkerResource(object):
    """Provides a way resolve :class:`scispacy.linking_utils.Entity` instances
    from CUIs.

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
        # should ahve no bearing since we're simply doing a CUI looking
        import warnings
        s = '.*Trying to unpickle estimator Tfidf(?:Transformer|Vectorizer) from version.*'
        warnings.filterwarnings('ignore', message=s)
        return EntityLinker(**self.params)

    def get_linked_entity(self, cui: str) -> Entity:
        """Get a scispaCy linked entity.

        :param cui: the unique concept ID

        """
        linker: EntityLinker = self.linker
        se: SciSpacyEntity = linker.kb.cui_to_entity.get(cui)
        if se is not None:
            return Entity(
                name=se.canonical_name,
                cui=se.concept_id,
                definition=se.definition,
                aliases=se.aliases,
                tuis=se.types)


@dataclass
class LinkFeatureTokenDecorator(FeatureTokenDecorator):
    """Adds linked SciSpacy definitions (when available) to tokens using the
    :class:`.MedicalLibrary`.

    """
    lib: MedicalLibrary = field(default=None)
    """The medical library used for linking entities."""

    feature_id: str = field(default='definition_')
    """The feature ID to use when adding linked entities (when available)."""

    feature_format: str = field(default="{definition}")
    """The formatting of the feature, which uses :meth:`.Entity.asdict` as the
    parameters available to the format.

    """
    def decorate(self, token: FeatureToken):
        e: SciSpacyEntity = self.lib.get_linked_entity(token.cui_)
        val: str = FeatureToken.NONE
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'entity: {token.cui_} -> {e} ({id(token)})')
        if e is not None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'entity: {e}')
            val = self.feature_format.format(**e.asdict())
            val = FeatureToken.NONE if val == 'None' else val
        token.set_feature(self.feature_id, val)

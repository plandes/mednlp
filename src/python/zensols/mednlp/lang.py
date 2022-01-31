from __future__ import annotations
"""Medical specific langauge resource.

"""
__author__ = 'Paul Landes'

from typing import Type, Union, Iterable, Dict, Optional, Any, Set, Tuple, List
from dataclasses import dataclass, field
import logging
from functools import reduce
import collections
from spacy.tokens.token import Token
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.language import Language
from scispacy.linking_utils import Entity as SciSpacyEntity
from medcat.cdb import CDB
from zensols.config import Dictable
from zensols.nlp import LanguageResource, TokenFeatures, SpacyTokenFeatures
from . import (
    MedNLPError, MedCatResource, EntityLinkerResource, UTSClient,
)

logger = logging.getLogger(__name__)


@dataclass
class Entity(Dictable):
    """A convenience container class that Wraps a SciSpacy entity.

    """
    _DICTABLE_ATTRIBUTES = 'cui name definition'.split()

    entity: SciSpacyEntity = field(repr=False)
    """The entity identified by :mod:`scispacy.linking_utils`."""

    @property
    def name(self) -> str:
        """The canonical name of the entity."""
        return self.entity.canonical_name

    @property
    def definition(self) -> str:
        """The human readable description of the entity."""
        return self.entity.definition

    @property
    def cui(self) -> str:
        """The unique concept identifier."""
        return self.entity.concept_id

    def __str__(self) -> str:
        return f'{self.name} ({self.cui})'

    def __repr__(self):
        return self.cui


@dataclass
class EntitySimilarity(Entity):
    """A similarity measure of a medical concept in cui2vec.

    :see: :meth:`.MedicalLanguageResource.similarity_by_term`
    """
    similiarty: float = field()


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


@dataclass
class MedicalTokenFeatures(SpacyTokenFeatures):
    """A set of token features that optionally contains a medical concept.

    """
    FIELD_IDS_BY_TYPE = {
        'str': frozenset('cui_ pref_name_ detected_name_ tuis_ definition_ tui_descs_'.split()),
        'bool': frozenset('is_concept'.split()),
        'float': frozenset('context_similarity'.split()),
        'int': frozenset('cui'.split()),
        'set': frozenset('tuis sub_names'.split()),
    }
    FIELD_IDS = frozenset(
        reduce(lambda res, x: res | x, FIELD_IDS_BY_TYPE.values()))
    NONE_SET = frozenset()

    def __init__(self, doc: Doc, tok_or_ent: Union[Token, Span], norm: str,
                 res: MedCatResource, ix2ent: Dict[int, _MedicalEntity]):
        super().__init__(doc, tok_or_ent, norm)
        self._definition: str = self.NONE
        self._cdb: CDB = res.cat.cdb
        self._res = res
        med_ent: Optional[_MedicalEntity] = ix2ent.get(self.i)
        if med_ent is None:
            med_ent = _MedicalEntity()
        self.is_ent = med_ent.is_ent
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
    def sub_names(self) -> Set[str]:
        """Return other names for the concept."""
        if self.is_concept:
            return self._cdb.cui2names[self.cui_]
        else:
            return self.NONE

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
        return self._definition

    @property
    def tuis(self) -> Set[str]:
        """The the CUI type of the concept."""
        if self.is_concept:
            cui: str = self.cui_
            return self._cdb.cui2type_ids.get(cui)
        else:
            return self.NONE_SET

    @property
    def tuis_(self) -> str:
        """All CUI TUIs (types) of the concept sorted as a comma delimited list.

        """
        return ','.join(sorted(self.tuis))

    @property
    def tui_descs_(self) -> str:
        """Descriptions of :obj:`tuis_`."""
        return ', '.join(map(lambda t: self._res.tuis[t], sorted(self.tuis)))

    def __str__(self):
        cui_str = f' ({self.cui_})' if self.is_concept else ''
        return self.norm + cui_str


@dataclass
class MedicalLanguageResource(LanguageResource):
    """A medical based language resources that parses concepts.

    """
    feature_type: Type[SpacyTokenFeatures] = field(
        default=MedicalTokenFeatures)
    """The class to use for instances created by :meth:`features`."""

    medcat_resource: MedCatResource = field(default=None)
    """The MedCAT factory resource."""

    entity_linker_resource: EntityLinkerResource = field(default=None)
    """The entity linker resource."""

    uts_client: UTSClient = field(default=None)
    """Queries UMLS data."""

    include_definition: bool = field(default=False)
    """If ``True``, include the concept definition in token features."""

    def __post_init__(self):
        if self.medcat_resource is None:
            raise MedNLPError('No medcat resource set')
        super().__post_init__()

    def _create_model_key(self) -> str:
        return 'name-{self.name}'

    def _create_model(self) -> Language:
        return self.medcat_resource.cat.get_spacy_nlp()

    def features(self, doc: Doc) -> Iterable[TokenFeatures]:
        def map_feature(t: Tuple[Token, str]):
            """Add linked definitions if enabled."""
            f: TokenFeatures = tf_type(doc, *t, res, ix2ent)
            if self.include_definition and f.is_concept:
                e: SciSpacyEntity = self.get_linked_entity(f.cui_)
                if e is not None:
                    f._definition = e.definition
            return f

        # load/create model resources
        res: MedCatResource = self.medcat_resource
        tf_type: Type[TokenFeatures] = self.feature_type
        ix2ent: Dict[int, _MedicalEntity] = collections.defaultdict(_MedicalEntity)

        # add entities
        for ent in doc.ents:
            for i in range(ent.start, ent.end):
                ix2ent[i].concept_span = ent

        return map(map_feature, self.token_normalizer.normalize(doc))

    def get_entities(self, text: str) -> Dict[str, Any]:
        """Return the all concept entity data

        :return: concepts as a multi-tiered dict

        """
        return self.medcat_resource.cat.get_entities(text)

    def get_linked_entity(self, cui: str) -> SciSpacyEntity:
        """Get a scispaCy linked entity.

        :param cui: the unique concept ID

        """
        se: SciSpacyEntity = self.entity_linker_resource.get_linked_entity(cui)
        if se is not None:
            return Entity(se)

    def get_atom(self, cui: str) -> Dict[str, str]:
        """Get the UMLS atoms of a CUI from UTS.

        :param cui: the concept ID used to query

        :param preferred: if ``True`` only return preferred atoms

        :return: a list of atom entries in dictionary form

        """
        return self.uts_client.get_atoms(cui, preferred=True)

    def get_relations(self, cui: str) -> List[Dict[str, Any]]:
        """Get the UMLS related concepts connected to a concept by ID.

        :param cui: the concept ID used to get related concepts

        :return: a list of relation entries in dictionary form in the order
                 returned by UTS

        """
        return self.uts_client.get_relations(cui)

    def get_new_ctakes_parser_stash(self) -> CTakesParserStash:
        """Return a new instance of a ctakes parser stash.

        """
        return self.config_factory.new_instance('ctakes_parser_stash')

    @property
    def cui2vec_embedding(self) -> Cui2VecEmbedModel:
        """The cui2vec embedding model.

        """
        return self.config_factory('cui2vec_500_embedding')

    def similarity_by_term(self, term: str, topn: int = 5) -> List[EntitySimilarity]:
        """Return similaries of a medical term.

        :param term: the medical term (i.e. ``heart disease``)

        :param topn: the top N count similarities to return

        """
        embedding: Cui2VecEmbedModel = self.cui2vec_embedding
        kv: KeyedVectors = embedding.keyed_vectors
        res: List[Dict[str, str]] = self.uts_client.search_term(term)
        cui: str = res[0]['ui']
        sims_by_word: List[Tuple[str, float]] = kv.similar_by_word(cui, topn)
        sims: List[EntitySimilarity] = []
        for rel_cui, proba in sims_by_word:
            entity: Entity = self.get_linked_entity(rel_cui)
            # name: str = entity.canonical_name.lower()
            # defn: str = entity.definition
            sim: float = embedding.keyed_vectors.similarity(cui, rel_cui)
            sims.append(EntitySimilarity(entity, sim))
        return sims

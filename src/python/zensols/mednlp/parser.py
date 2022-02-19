from __future__ import annotations
"""Medical specific langauge resource.

"""
__author__ = 'Paul Landes'

from typing import Type, Iterable, Dict, Any, Tuple, List
from dataclasses import dataclass, field
import logging
import collections
from spacy.tokens.token import Token
from spacy.tokens.doc import Doc
from spacy.language import Language
from scispacy.linking_utils import Entity as SciSpacyEntity
from zensols.config import ConfigFactory
from zensols.nlp import FeatureToken, MappingCombinerFeatureDocumentParser
from . import (
    MedNLPError, MedCatResource, MedicalFeatureToken,
    EntityLinkerResource, UTSClient
)
from .domain import Entity, _MedicalEntity, EntitySimilarity

logger = logging.getLogger(__name__)


@dataclass
class MedicalFeatureDocumentParser(MappingCombinerFeatureDocumentParser):
    """A medical based language resources that parses concepts.

    """
    config_factory: ConfigFactory = field(default=None)
    """The configuration factory used to create cTAKES and cui2vec instances."""

    token_class: Type[FeatureToken] = field(default=MedicalFeatureToken)
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
        return f'name-{self.name}'

    def _create_model(self) -> Language:
        return self.medcat_resource.cat.get_spacy_nlp()

    def _create_token(self, tok: Token, norm: Tuple[Token, str],
                      *args, **kwargs) -> FeatureToken:
        tp: Type[FeatureToken] = self.token_class
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
            sims.append(EntitySimilarity(entity.sci_spacy_entity, sim))
        return sims

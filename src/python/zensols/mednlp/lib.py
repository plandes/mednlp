from __future__ import annotations
"""Medical resource library that contains UMLS access, cui2vec etc..

"""
__author__ = 'Paul Landes'

from typing import Any, List, Dict, Tuple
from dataclasses import dataclass, field
from zensols.config import ConfigFactory
from . import MedCatResource, UTSClient


@dataclass
class MedicalLibrary(object):
    """A utility class that provides access to medical APIs.

    """
    config_factory: ConfigFactory = field(default=None)
    """The configuration factory used to create cTAKES and cui2vec instances.

    """
    medcat_resource: MedCatResource = field(default=None)
    """The MedCAT factory resource."""

    entity_linker_resource: 'EntityLinkerResource' = field(default=None)
    """The entity linker resource."""

    uts_client: UTSClient = field(default=None)
    """Queries UMLS data."""

    def get_entities(self, text: str) -> Dict[str, Any]:
        """Return the all concept entity data.

        :return: concepts as a multi-tiered dict

        """
        return self.medcat_resource.cat.get_entities(text)

    def get_linked_entity(self, cui: str) -> 'Entity':
        """Get a scispaCy linked entity.

        :param cui: the unique concept ID

        """
        from scispacy.linking_utils import Entity as SciSpacyEntity
        from .entlink import Entity
        ent: Entity = self.entity_linker_resource.get_linked_entity(cui)
        return ent

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

    def similarity_by_term(self, term: str, topn: int = 5) -> \
            List['EntitySimilarity']:
        """Return similaries of a medical term.

        :param term: the medical term (i.e. ``heart disease``)

        :param topn: the top N count similarities to return

        """
        from .entlink import Entity, EntitySimilarity
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

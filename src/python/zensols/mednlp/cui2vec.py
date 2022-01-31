"""This module contains the embedding subclass for cui2vec embeddings.

"""
__author__ = 'Paul Landes'

from typing import Dict, List
from dataclasses import dataclass, field
import logging
import csv
from h5py import Dataset
from zensols.deepnlp.embed import (
    WordEmbedError, TextWordEmbedModel, TextWordModelMetadata
)

logger = logging.getLogger(__name__)


@dataclass
class Cui2VecEmbedModel(TextWordEmbedModel):
    """This class uses the pretrained cui2vec embeddings.

    """
    dimension: str = field(default=500)
    """The word vector dimension."""

    vocab_size: int = field(default=109053)
    """Vocabulary size."""

    def _populate_vec_lines(self, words: List[str], word2idx: Dict[str, int],
                            ds: Dataset):
        idx = 0
        lc = 0
        meta = self.metadata
        with open(meta.source_path) as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for rix, line in enumerate(csv_reader):
                lc += 1
                word = line[0]
                words.append(word)
                word2idx[word] = idx
                idx += 1
                try:
                    ds[rix, :] = tuple(map(float, line[1:]))
                except Exception as e:
                    raise WordEmbedError(
                        f'Could not parse line {lc} (word: {word}): ' +
                        f'{e}; line: {line}') from e

    def _get_metadata(self) -> TextWordModelMetadata:
        name = 'cui2vec'
        dim = self.dimension
        path = self.path.parent / self.resource.check_path
        return TextWordModelMetadata(
            name, 'default', dim, self.vocab_size, path,
            sub_directory='cui2vec-bin')

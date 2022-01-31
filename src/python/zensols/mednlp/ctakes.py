"""Parse and normalize discharge notes.

"""
__author__ = 'Paul Landes'

from typing import Iterable
from dataclasses import dataclass, field
import logging
import os
from pathlib import Path
import pandas as pd
from zensols.config import Dictable
from zensols.persist import Stash, DirectoryStash, ReadOnlyStash, Primeable
from zensols.util.executor import Executor
import ctakes_parser.ctakes_parser as ctparser
from . import MedNLPError

logger = logging.getLogger(__name__)
ctakes_logger = logging.getLogger(__name__ + '.ctakes')


@dataclass
class _TextDirectoryStash(DirectoryStash):
    pattern: str = field(default='{name}.txt')

    def _load_file(self, path: Path) -> str:
        with open(path, 'r') as f:
            return f.read()

    def _dump_file(self, inst: str, path: Path):
        with open(path, 'w') as f:
            f.write(inst)


@dataclass
class CTakesParserStash(ReadOnlyStash, Primeable, Dictable):
    """Runs the cTAKES CUI entity linker on a directory of medical notes.  For each
    medical text file, it generates an ``xmi`` file, which is then parsed by
    the the :mod:`ctakes_parser` library.

    This straightforward wrapper around the ``ctparser`` library automates the
    file system orchestration that needs to happen.  Configure an instance of
    this class as an application configuration and use a
    :class:`~zensols.config.ImportConfigFactory` to create the objects.  See
    the ``examples/ctakes`` directory for a quick start guide on how to use
    this class.

    """
    entry_point_bin: Path = field()
    """Entry point script in to the cTAKES parser."""

    entry_point_cmd: str = field()
    """Command line arguments passed to cTAKES."""

    home: Path = field()
    """The directory where cTAKES is installed."""

    source_dir: Path = field()
    """Contains a path to the source directory where the text documents live.

    """
    output_dir: Path = field(default=None)
    """The directory where to output the xmi files."""

    def __post_init__(self):
        super().__post_init__()
        self.strict = True
        self._pattern: str = field(default='{name}.txt.xmi')
        if self.output_dir is None:
            self.output_dir = self.source_dir.parent / 'output'
        for attr in 'entry_point_bin source_dir output_dir'.split():
            setattr(self, attr, getattr(self, attr).absolute())
        self._source_stash = _TextDirectoryStash(self.source_dir)
        self._out_stash = _TextDirectoryStash(
            path=self.output_dir,
            pattern=self._source_stash.pattern + '.xmi')

    @property
    def source_stash(self) -> Stash:
        """The stash that tracks the text documents that are to be parsed by cTAKES.

        """
        return self._source_stash

    def set_documents(self, docs: Iterable[str]):
        """Set the document to be parsed by cTAKES.

        :param docs: an iterable of string text documents to persist to the
                     file system, and then be parsed by cTAKES.

        """
        self.clear()
        for i, doc in enumerate(docs):
            self._source_stash.dump(str(i), doc)

    def _run(self):
        """Run cTAKES (see class docs)."""
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'running ctakes parser on {self.source_dir}')
        os.environ['CTAKES_HOME'] = str(self.home.absolute())
        cmd = self.entry_point_cmd.format(**self.asdict())
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'executing {cmd}')
        exc = Executor(ctakes_logger)
        exc.run(cmd)

    def prime(self):
        super().prime()
        if not self.source_dir.is_dir():
            raise MedNLPError('cTAKES temporary path is not an existing ' +
                              f'directory: {self.source_dir}')
        if len(self._source_stash) == 0:
            raise MedNLPError(
                f'Source directory contains no data: {self.source_dir}')
        if len(self._out_stash) == 0:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self._run()

    def load(self, name: str) -> pd.DataFrame:
        self.prime()
        path: Path = self._out_stash.key_to_path(name)
        return ctparser.parse_file(file_path=str(path))

    def keys(self) -> Iterable[str]:
        self.prime()
        return self._out_stash.keys()

    def exists(self, name: str) -> bool:
        self.prime()
        return self._out_stash.exists(name)

    def clear(self):
        self._out_stash.clear()
        self._source_stash.clear()

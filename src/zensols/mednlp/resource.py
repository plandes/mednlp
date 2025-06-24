"""MedCAT wrapper.

"""
__author__ = 'Paul Landes'

from typing import Tuple, Dict, Any, Set
from dataclasses import dataclass, field, InitVar
import logging
from pathlib import Path
import re
from frozendict import frozendict
import pandas as pd
from medcat.config import Config, MixingConfig
from medcat.vocab import Vocab
from medcat.cdb import CDB
from medcat.cat import CAT
from medcat.meta_cat import MetaCAT
from zensols.util.package import PackageRequirement, PackageManager
from zensols.config import Dictable
from zensols.persist import persisted, PersistedWork
from zensols.install import Resource, Installer

logger = logging.getLogger(__name__)


@dataclass
class MedCatResource(Dictable):
    """A factory class that creates MedCAT resources.

    """
    _MODEL_REGEX = re.compile(r'^([^@]+) @ .+$')
    """A regular expression for a spaCy model dependency (http syntax)."""

    installer: Installer = field()
    """Installs and provides paths to the model files."""

    vocab_resource: Resource = field()
    """The path to the ``vocab.dat`` file."""

    cdb_resource: Resource = field()
    """The ``cdb-medmen-v1.dat`` file.

    """
    mc_status_resource: Resource = field()
    """The the ``mc_status`` directory.

    """
    umls_tuis: Resource = field()
    """The UMLS TUIs (types) mapping resource that maps from TUIs to
    descriptions.

    :see: `Semantic Types <https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/SemanticTypesAndGroups.html>`_

    """
    umls_groups: Resource = field()
    """Like :obj:`umls_tuis` but groups TUIs in gropus."""

    filter_tuis: Set[str] = field(default=None)
    """Types used to filter linked CUIs (i.e. ``{'T047', 'T048'}``).

    """
    filter_groups: Set[str] = field(default=None)
    """Just like :obj:`filter_tuis` but each element is treated as a group used
    to generate a list of CUIs from those mapped from ``name`` to ``tui` in
    :obj:`groups`.

    """
    spacy_enable_components: Set[str] = field(
        default_factory=lambda: set('sentencizer parser'.split()))
    """By default, MedCAT disables several pipeline components.  Some of these
    are needed for sentence chunking and other downstream tasks.  Otherwise
    sentence indexing won't work because sentence boundaries are missing.

    :see: `MedCAT Config <https://github.com/CogStack/MedCAT/blob/master/medcat/config.py>`_

    """
    cat_config: Dict[str, Dict[str, Any]] = field(default=None)
    """If provieded, set the CDB configuration.  Keys are ``general``,
    ``preprocessing`` and all other attributes documented in the `MedCAT Config
    <https://github.com/CogStack/MedCAT/blob/master/medcat/config.py>`_

    """
    cache_global: InitVar[bool] = field(default=True)
    """Whether or not to globally cache resources, which saves load time.

    """
    requirements: Tuple[str, ...] = field(default=())
    """A list of spaCy pip dependencies (can include model direct-references)
    that will be installed if not already.

    """
    package_manager: PackageManager = field(default_factory=PackageManager)
    """The package manager used to install :obj:`requirements`."""

    def __post_init__(self, cache_global: bool):
        self._tuis = PersistedWork('_tuis', self, cache_global=cache_global)
        self._cat = PersistedWork('_cat', self, cache_global=cache_global)
        self._installed = False

    @staticmethod
    def _filter_medcat_logger():
        class NoCdbExportFilter(logging.Filter):
            def filter(self, record):
                s = 'The CDB was exported by an unknown version of MedCAT.'
                return not record.getMessage() == s

        logging.getLogger('medcat.cdb').addFilter(NoCdbExportFilter())

    def _assert_installed(self):
        if not self._installed:
            self.installer()
            self._installed = True

    def _override_config(self, targ: Config, src: Dict[str, Dict[str, Any]]):
        src_top: str
        src_conf = Dict[str, Any]
        for src_top, src_conf in src.items():
            targ_any: Any = getattr(targ, src_top)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"updating dict '{src_top}' ({type(targ_any)}): " +
                             f"<{targ_any}> with <{src_conf}>")
            if isinstance(targ_any, dict):
                targ_any.update(src_conf)
            elif isinstance(targ_any, MixingConfig):
                targ_any.merge_config(src_conf)
            else:
                setattr(targ, src_top, src_conf)

    def _add_filters(self, config: Config, cdb: CDB):
        filter_tuis = set()
        if self.filter_tuis is not None:
            filter_tuis.update(self.filter_tuis)
        if self.filter_groups is not None:
            df: pd.DataFrame = self.groups
            reg = '.*(' + '|'.join(self.filter_groups) + ')'
            df = df[df['name'].str.match(reg)]
            filter_tuis.update(df['tui'].tolist())
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'filtering on tuis: {", ".join(filter_tuis)}')
        if len(filter_tuis) > 0:
            cui_filters = set()
            for tui in filter_tuis:
                cui_filters.update(cdb.addl_info['type_id2cuis'][tui])
            config.linking['filters']['cuis'] = cui_filters

    @property
    @persisted('_tuis')
    def tuis(self) -> Dict[str, str]:
        """A mapping of type identifiers (TUIs) to their descriptions."""
        self._assert_installed()
        path: Path = self.installer[self.umls_tuis]
        df = pd.read_csv(path, delimiter='|', header=None)
        df.columns = 'abbrev tui desc'.split()
        df_tups = df[['tui', 'desc']].itertuples(name=None, index=False)
        return frozendict(df_tups)

    @property
    @persisted('_groups')
    def groups(self) -> pd.DataFrame:
        """A dataframe of TUIs, their abbreviations, descriptions and a group
        name associated with each.

        """
        self._assert_installed()
        path: Path = self.installer[self.umls_groups]
        df = pd.read_csv(path, delimiter='|', header=None)
        df.columns = 'abbrev name tui desc'.split()
        return df

    @property
    @persisted('_cat')
    def cat(self) -> CAT:
        """The MedCAT NER tagger instance.

        When this property is accessed, all models are downloaded first, then
        loaded, if not already.

        """
        # install medcat models if not already
        self._assert_installed()
        # ensure models are installed
        self._assert_requirements()
        # Load the vocab model you downloaded
        vocab = Vocab.load(self.installer[self.vocab_resource])
        # Load the cdb model you downloaded
        cdb = CDB.load(self.installer[self.cdb_resource])
        # mc status model
        mc_status = MetaCAT.load(self.installer[self.mc_status_resource])
        # enable sentence boundary annotation
        for name in self.spacy_enable_components:
            cdb.config.general['spacy_disabled_components'].remove(name)
        # override configuration
        if self.cat_config is not None:
            self._override_config(cdb.config, self.cat_config)
        # add TUI filters (i.e. filter out non-medical terms)
        self._add_filters(cdb.config, cdb)
        # create cat - each cdb comes with a config that was used to train it;
        # you can change that config in any way you want, before or after
        # creating cat
        return CAT(cdb=cdb, config=cdb.config, vocab=vocab,
                   meta_cats=[mc_status])

    def _assert_requirements(self):
        spec: str
        for spec in self.requirements:
            req = PackageRequirement.from_spec(spec)
            self.package_manager.install(req)

    def clear(self):
        self._tuis.clear()
        self._cat.clear()


MedCatResource._filter_medcat_logger()

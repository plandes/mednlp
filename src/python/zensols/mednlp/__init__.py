def _intercept_medcat_logging():
    """Cludge to stop medcat from creating the ``medcat.log`` file.

    """
    import medcat.utils.loggers
    import logging

    def add_medcat_logger(logger: logging.Logger):
        return logger

    medcat.utils.loggers.add_handlers = add_medcat_logger


_intercept_medcat_logging()


from zensols.util import APIError


class MedNLPError(APIError):
    """Raised by any medical NLP speicic reason in this library."""
    pass


from .uts import UTSError, NoResultsError, AuthenticationError, UTSClient
from .resource import *
from .lang import *
from .app import *
from .cli import *

import sys
from loguru import logger as _logger

_logger.remove()
_logger.add(
    sys.stdout,
    format=(
        """<green>{time:YYYY-MM-DD HH:mm:ss}</green> | """
        """<level>{level}</level> | """
        """<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | """
        """<level>{message}</level> | """
    ),
    level="INFO",
    backtrace=True,
    diagnose=True,
)

logger = _logger.bind(name="hi man")

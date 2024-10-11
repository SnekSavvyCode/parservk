import logging

__all__ = ["_logger"]

LEVEL = logging.INFO
FORMAT = (
    "[%(asctime)s] %(levelname)s %(name)s %(message)s"
)
DATEFMT = "%Y.%m.%d %X"

logging.basicConfig(level=LEVEL, format=FORMAT, datefmt=DATEFMT)

_logger = logging.getLogger
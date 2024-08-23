import logging

__all__ = ["LOGGER"]

LEVEL = logging.INFO
FORMAT = "[%(levelname)-7s] [%(asctime)s]  [%(name)-10s] in line %(lineno)-3s - %(message)s"
DATEFMT = "%Y.%m.%d %H:%M:%S"

logging.basicConfig(level=LEVEL, format=FORMAT, datefmt=DATEFMT)

LOGGER = logging.getLogger(__name__)

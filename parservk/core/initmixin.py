import logging

from .logger import _logger
from .poolmanager import PoolManager
from .handlers.handlers import Handlers
from .utils import method_from_class

class InitMixin:
    
    fields_list = []

    def __init__(self, parser, logger: logging.Logger = _logger) -> None:
        """
        Initialize the mixin with the provided parser and logger.

        :param parser: The parser object used for parsing data.
        :param logger: The logger object for logging messages. Default is _logger.
        """

        self.parser = parser
        self.poolmanager = PoolManager()
        self.handlers = Handlers(PoolManager(), self.parser)
        self.tokens = self.parser.tokens
        self.v = self.parser.v_api
        self.headers = self.parser.headers
        self.proxies = self.parser.proxies
        self.base_params = {
            "access_token": list(self.tokens)[0],
            "v": self.v,
        }
        self.__class__._NAME = getattr(self, "_NAME", self.__class__.__name__.upper())
        self.logger = logger(f"{self.__module__}.{self._NAME.title()}")
        self._limits = getattr(self, "_limits", {})
        self._methods, self._limits_per_category = self.create_methods_and_limits()
        self.FIELDS = ", ".join(self.fields_list)
        	
    def create_methods_and_limits(self) -> tuple[dict]:
    	"""
        Create methods and limits for the mixin based on child classes.

        :return: A tuple containing a dictionary of methods and a dictionary of limits per category.
        """

    	methods = {}
    	limits_per_category = {}
    	for child_class in type(self).__bases__[0].__subclasses__():
    		methods[child_class._NAME] = method_from_class(child_class)
    		limits_per_category[child_class._NAME] = child_class._limits
    	
    	return methods, limits_per_category
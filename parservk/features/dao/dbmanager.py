import json

from logging import Logger
from typing import Optional, Union, Any

from sqlalchemy import create_engine, Engine, MetaData
from sqlalchemy.orm import declarative_base, DeclarativeMeta, sessionmaker

from ...core import _logger
from .dynamictablemeta import DynamicTableMeta
from .models import DataModel, DBSettings

class DBManager:
    """
    Database manager class
    """
    DIALECTS = ["sqlite", "postgresql", "mysql"]
    DRIVERS = {"sqlite": {}, "postgresql": {}, "mysql": {}}
    URL_FOR_DIALECT = {
        "sqlite": "{}:///{}",
        "postgresql": "{}://{}:{}@{}:{}/{}",
        "mysql": "{}://{}:{}@{}:{}/{}"
    }

    def __init__(
        self,
        database: str,
        dialect: str = "sqlite",
        driver: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: str = "localhost",
        port: int = 8000,
        settings: DBSettings = DBSettings(),
        logger: Logger = _logger
    ):
        """
        Initialize database manager

        :param database: database name
        :param dialect: database dialect (sqlite, postgresql, mysql)
        :param driver: database driver (optional)
        :param username: database username (optional)
        :param password: database password (optional)
        :param host: database host (optional)
        :param port: database port (optional)
        :param settings: database settings (optional)
        """
        self.database = database
        self.dialect = dialect
        self.driver = driver
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.settings = settings
        self._url = self._create_url(
            database, dialect, username=username, password=password, host=host, port=port, driver=driver
        )
        self._declarative_meta = declarative_base()
        self._metadata = self._declarative_meta.metadata
        self._engine = self._create_engine(self.settings)
        self.Session = sessionmaker(bind=self._engine, autoflush=False)
        self.LOGGER = logger

    def _create_url(self, *args, **kwargs) -> str:
        """
        Create database url

        :param args: database name and dialect
        :param kwargs: additional parameters (username, password, host, port, driver)
        :return: database url
        """
        database = args[0]
        driver = kwargs.get("driver")
        dialect = args[1].lower()
        if dialect not in self.DIALECTS:
            raise ValueError(f"Dialect {dialect} not found")
        dialect_driver = dialect
        if driver:
            dialect_driver = f"{dialect}+{driver}"
        username = kwargs.get("username")
        password = kwargs.get("password")
        host = kwargs.get("host")
        port = kwargs.get("port")
        if dialect == "sqlite":
            url = self.URL_FOR_DIALECT.get(dialect).format(dialect_driver, database)
        else:
            url = self.URL_FOR_DIALECT.get(dialect).format(
                dialect_driver, username, password, host, port, database
            )
        return url

    def _create_engine(self, settings: DBSettings) -> Engine:
        """
        Create database engine

        :return: database engine
        """
        try:
            settings_dict = {key.lower(): value for key, value in json.loads(settings.json()).items()}
            return create_engine(self._url, **settings_dict)
        except ModuleNotFoundError as e:
            self.LOGGER.error(f"Error creating engine: {e}")
    def create_table(self, isclass: bool =True, nameclass: Optional[str] = None, bases: tuple = (), **kwargs):
     	self.LOGGER.warning("The method in development")
     	if isclass:
     		if not nameclass: nameclass = kwargs.get("__tablename__", "")
     		if not bases: bases = (self._declarative_meta,)
     		return DynamicTableMeta(nameclass, bases, kwargs)
     	else:
     		...

    @property
    def engine(self) -> Engine:
        """Get database engine"""
        return self._engine

    @engine.setter
    def engine(self, engine: Engine):
        if not isinstance(engine, Engine):
            raise ValueError(f"The Engine type was expected, not {engine.__class__.__name__}")
        self._engine = engine
        return self._engine
        
    @property
    def metadata(self) -> MetaData:
    	"""Get database metadata"""
    	return self._metadata
    
    @metadata.setter
    def metadata(self, metadata: Union[MetaData, DeclarativeMeta]) -> MetaData:
    	if not isinstance(metadata, (MetaData, DeclarativeMeta)):
    		raise ValueError(f"The MetaData or DeclarativeMeta type was expected, not {metadata.__class__.__name__}")
    	if isinstance(metadata, MetaData):
    		self.LOGGER.warning("The declarative_meta attribute and metadata are linked. This can lead to errors. It is better to use the DeclarativeMeta class")
    		self._metadata = metadata
    		return self._metadata
    		
    	self._declarative_class = metadata
    	self._metadata = self._declarative_class.metadata
    	return self._metadata
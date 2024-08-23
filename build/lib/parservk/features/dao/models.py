from typing import Any

from pydantic import BaseModel, BaseSettings

class DataModel(BaseModel):
	"""
	A data model for creating dynamic tables
	
	:param type: column type
	:param params: settings params for mapped_column from sqlalchemy (dict)
	"""
	
	type: Any
	params: dict = {}

class DBSettings(BaseSettings):
    """
    Settings for database connection

    :param pool_size: The size of the database connection pool
    :param max_overflow: The maximum number of connections to allow in the pool
    :param pool_timeout: The timeout for waiting for a connection from the pool
    :param pool_recycle: The interval at which to recycle connections in the pool
    :param echo: Whether to echo database queries
    :param echo_pool: Whether to echo pool-related messages
    :param isolation_level: The isolation level for database transactions
    """

    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    echo_pool: bool = False
    isolation_level: str = "AUTOCOMMIT"

    class Config:
        """
        Configuration settings

        :param env_file: The file path to load environment variables from
        :param env_file_encoding: The encoding to use when reading the environment file
        """
        env_file = ".env"
        env_file_encoding = "UTF-8"
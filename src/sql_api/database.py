"""This module is responsible for the database connection and session creation

This module is responsible for the database connection and session creation. It
also provides a function to get the session maker object.

Example:
    To use this module, you need to call the init_db function with the database
    URL as an argument. Then you can call the get_maker function to get the session
    maker object.

    >>> import database
    >>> database.init_db("sqlite:///test.db")
    >>> maker = database.get_maker()
    >>> session = maker()
    >>> session.query(User).all()

This modules manages the database connection and session creation. It also provides
a function to get the session maker object.

Functions:
    - init_db: Initialize the database connection
    - get_maker: Get the session maker object

Classes:
    - Api: The base class for the database models

Attributes:
    - maker: The session maker object
"""
import inspect

import sqlalchemy as sa
import sqlalchemy.orm as orm

maker: orm.sessionmaker | None = None

Api = orm.declarative_base()


def init_db(config: str):
    """Initialize the database connection

    This function initializes the database connection. It takes the database URL
    as an argument and creates a session maker object.

    Args:
        config (str): The database URL

    Returns:
        None
    """
    global maker
    url = config
    engine = sa.create_engine(url)
    maker = orm.sessionmaker(autocommit=False,
                             autoflush=False,
                             bind=engine,
                             info={},
                             close_resets_only=False)


def get_maker():
    """Get the session maker object

    This function returns the session maker object. It is used to create a new
    session object to interact with the database.

    Returns:
        orm.sessionmaker: The session maker object

    Raises:
        Exception: If the database is not initialized
    """
    global maker
    if maker is None:
        raise Exception("You need to init the db by giving me a valid URL")
    caller = inspect.currentframe().f_back.f_code.co_qualname
    file = inspect.currentframe().f_back.f_code.co_filename
    line = inspect.currentframe().f_back.f_code.co_firstlineno
    maker.kw["info"]["caller"] = caller
    maker.kw["info"]["file"] = f"{file}:{line}"
    return maker

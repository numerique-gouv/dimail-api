"""This module is used to initialize the database and get the session maker

The database is initialized by calling the init_db function with the url of the database.
The get_maker function is used to get the session maker to interact with the database.

Classes:
    Postfix: The base class for the database models.

Functions:
    init_db: Initialize the database with the given url.
    get_maker: Get the session maker to interact with the database.

Variables:
    maker: The session maker to interact with the database.
"""
import inspect

import sqlalchemy as sa
import sqlalchemy.orm as orm

maker: orm.sessionmaker | None = None

Postfix = orm.declarative_base()


def init_db(config: str):
    """Initialize the database with the given url.

    Args:
        config: The url of the database
    """
    global maker
    url = config
    engine = sa.create_engine(url)
    maker = orm.sessionmaker(autocommit=False,
                             autoflush=False,
                             bind=engine,
                             info={},
                             close_resets_only=False)


def get_maker() -> orm.sessionmaker:
    """Get the session maker to interact with the database.

    Returns:
        The session maker to interact with the database.

    Raises:
        Exception: If the database is not initialized.
    """
    global maker
    if maker is None:
        raise Exception("Please init the postfix database by giving me an url...")
    caller = inspect.currentframe().f_back.f_code.co_qualname
    file = inspect.currentframe().f_back.f_code.co_filename
    line = inspect.currentframe().f_back.f_code.co_firstlineno
    maker.kw["info"]["caller"] = caller
    maker.kw["info"]["file"] = f"{file}:{line}"
    return maker


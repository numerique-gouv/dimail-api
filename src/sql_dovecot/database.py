"""This module is used to initialize the database and get the session maker.

Classes:
    - Dovecot: the base class for the database models

Functions:
    - init_db: initialize the database
    - get_maker: get the session maker

Variables:
    - maker: the session maker
"""
import inspect

import sqlalchemy as sa
import sqlalchemy.orm as orm

maker: orm.sessionmaker | None = None

Dovecot = orm.declarative_base()


def init_db(config: str):
    """Initialize the database.

    Args:
        config (str): the configuration of the database

    Returns:
        None
    """
    # global url
    # global engine
    global maker
    url = config
    engine = sa.create_engine(url)
    maker = orm.sessionmaker(autocommit=False,
                             autoflush=False,
                             bind=engine,
                             info={},
                             close_resets_only=False)


def get_maker() -> orm.sessionmaker:
    """Get the session maker.

    Returns:
        orm.sessionmaker: the session

    Raises:
        Exception: if the database is not initialized
    """
    global maker
    if maker is None:
        raise Exception("Please init the database by giving me an url...")
    caller = inspect.currentframe().f_back.f_code.co_qualname
    file = inspect.currentframe().f_back.f_code.co_filename
    line = inspect.currentframe().f_back.f_code.co_firstlineno
    maker.kw["info"]["caller"] = caller
    maker.kw["info"]["file"] = f"{file}:{line}"
    return maker


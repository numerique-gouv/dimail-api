import logging
import os
import typing

import pytest
import sqlalchemy as sa
import sqlalchemy.orm as orm

import alembic.command
import alembic.config

from . import sql_api
from . import sql_dovecot


@pytest.fixture(scope="session", name="log")
def fix_logger(scope="session") -> typing.Generator:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info("SETUP logger")
    yield logger
    logger.info("TEARDOWN logger")


@pytest.fixture(scope="session")
def root_db(log) -> typing.Generator:
    log.info("CONNECTING as mysql root")
    root_db = sa.create_engine("mysql+pymysql://root:toto@localhost:3306/mysql")
    conn = root_db.connect()
    yield conn
    conn.close()
    log.info("CLOSING root mysql connection")


def make_db(name: str, conn: sa.Engine) -> str:
    conn.execute(sa.text(f"drop database if exists {name};"))
    conn.execute(sa.text(f"create database {name};"))
    conn.execute(sa.text(f"grant ALL on {name}.* to test@'%' identified by 'toto';"))
    return f"mysql+pymysql://test:toto@localhost:3306/{name}"


def drop_db(name: str, conn: sa.Engine):
    conn.execute(sa.text(f"drop database if exists {name};"))


@pytest.fixture(scope="session")
def ensure_db_api(root_db, alembic_config, log) -> typing.Generator:
    log.info("SETUP api database (drop and create)")
    url = make_db("test", root_db)
    before = set_alembic_url(alembic_config, "api", url, log)
    yield url
    alembic_config.set_main_option("databases", before)
    drop_db("test", root_db)
    log.info("TEARDOWN api database (drop)")


@pytest.fixture(scope="session")
def ensure_db_dovecot(root_db, alembic_config, log) -> typing.Generator:
    log.info("SETUP dovecot database (drop and create)")
    url = make_db("test2", root_db)
    before = set_alembic_url(alembic_config, "dovecot", url, log)
    yield url
    alembic_config.set_main_option("databases", before)
    drop_db("test2", root_db)
    log.info("TEARDOWN dovecot database (drop)")


@pytest.fixture(scope="session")
def alembic_config(log) -> typing.Generator:
    log.info("SETUP alembic config")
    if not os.path.exists("alembic.ini"):
        raise Exception("Je veux tourner dans src, avec mon fichier alembic.ini")
    cfg = alembic.config.Config("alembic.ini")
    cfg.set_main_option("databases", "")
    cfg.set_main_option("init_logger", "False")
    # cfg.set_section_option("api", "sqlalchemy.url", 'mysql+pymysql://test:toto@localhost:3306/test')
    # cfg.set_section_option("dovecot", "sqlalchemy.url", 'mysql+pymysql://test:toto@localhost:3306/test2')
    yield cfg
    log.info("TEARDOWN alembic config")


def set_alembic_url(alembic_config, db_name: str, db_url: str, log):
    before = alembic_config.get_main_option("databases")
    if before == "":
        log.info(f"{db_name} is alone")
        alembic_config.set_main_option("databases", db_name)
    else:
        log.info(f"{db_name} is added to {before}")
        alembic_config.set_main_option("databases", f"{before}, {db_name}")
    alembic_config.set_section_option(db_name, "sqlalchemy.url", db_url)
    return before


@pytest.fixture(scope="function")
def alembic_run(alembic_config, log) -> typing.Generator:
    log.info("SETUP with alembic (upgrade)")
    bases = alembic_config.get_main_option("databases")
    log.info(f" - Here are the databases : {bases}")
    alembic.command.upgrade(alembic_config, "head")
    yield
    bases = alembic_config.get_main_option("databases")
    alembic.command.downgrade(alembic_config, "base")
    log.info("TEARDOWN with alembic (downgrade)")
    log.info(f" - Here are the databases : {bases}")


@pytest.fixture(scope="function")
def db_api(alembic_run, ensure_db_api, log) -> typing.Generator:
    log.info("SETUP sql_api to use the testing db")
    sql_api.init_api_db(ensure_db_api)
    yield

@pytest.fixture(scope="function")
def db_dovecot(alembic_run, ensure_db_dovecot, log) -> typing.Generator:
    log.info("SETUP sql_dovecot to use the testing db")
    sql_dovecot.init_dovecot_db(ensure_db_dovecot)
    yield 


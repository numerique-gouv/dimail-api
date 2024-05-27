import logging
import os
import typing

import alembic.command
import alembic.config
import pytest
import sqlalchemy as sa

import alembic.command
import alembic.config

from . import oxcli, sql_api, sql_dovecot, sql_postfix
from testcontainers.mysql import MySqlContainer

from . import oxcli, sql_api, sql_dovecot


def make_db(name: str, conn: sa.Connection) -> str:
    """Utility function, for internal use. Ensure a database, named 'name'
    is created and empty. 'conn' is a mariadb/mysql connection as root user"""
    return make_db_with_user(name, "test", "toto", conn)


def make_db_with_user(name: str, user: str, password: str, conn: sa.Connection) -> str:
    """Utility function, for internal use. Ensure a database, named 'name'
    is created and empty. 'conn' is a mariadb/mysql connection as root user"""
    conn.execute(sa.text(f"drop database if exists {name};"))
    conn.execute(sa.text(f"create database {name};"))
    conn.execute(sa.text(f"grant ALL on {name}.* to {user}@'%' identified by '{password}';"))
    mariadb_port = conn.engine.url.port
    return f"mysql+pymysql://{user}:{password}@localhost:{mariadb_port}/{name}"


def drop_db(name: str, conn: sa.Engine):
    """Utility function, for internal use. Drops a database."""
    conn.execute(sa.text(f"drop database if exists {name};"))


@pytest.fixture(scope="session", name="log")
def fix_logger(scope="session") -> typing.Generator:
    """Fixture making the logger available"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info("SETUP logger")
    yield logger
    logger.info("TEARDOWN logger")


@pytest.fixture(scope="session")
def mariadb_container(log, request):
    mysql = MySqlContainer("mariadb:11.2", username="root", password="toto", dbname="mysql")
    log.info("SETUP MARIADB CONTAINER")
    mysql.start()

    def remove_container():
        mysql.stop()
        log.info("TEARDOWN MARIADB CONTAINER")

    request.addfinalizer(remove_container)
    return mysql


@pytest.fixture(scope="module")
def engine(mysql_container):
    engine = sa.create_engine(mysql_container.get_connection_url())
    engine.connect()
    engine.begin
    yield engine


@pytest.fixture(scope="session")
def root_db(log, mariadb_container) -> typing.Generator:
    """Fixtures that makes a connection to mariadb/mysql as root available."""
    log.info("CONNECTING as mysql root")
    root_db = sa.create_engine(mariadb_container.get_connection_url())
    conn = root_db.connect()
    yield conn
    conn.close()
    log.info("CLOSING root mysql connection")


# @pytest.fixture(scope="session")
# def mariadb_port(log, mariadb_container) -> int:
#     """Fixtures that exposes port for random mariadb container."""
#     log.info(f"type of mariadb container: {type(mariadb_container)}")
#     log.info(f"type of mariadb container port: {type(mariadb_container.port)}")
#     return mariadb_container.port


@pytest.fixture(scope="session")
def alembic_config(log) -> typing.Generator:
    """Fixtures that makes available the alambic config, for future use. The
    list of databases is made empty. Alembic is told not to do anything to
    the logger, so that we can have logs where we want them."""
    log.info("SETUP alembic config")
    if not os.path.exists("alembic.ini"):
        raise Exception("Je veux tourner dans src, avec mon fichier alembic.ini")
    cfg = alembic.config.Config("alembic.ini")
    cfg.set_main_option("databases", "")
    cfg.set_main_option("init_logger", "False")
    yield cfg
    log.info("TEARDOWN alembic config")


def add_db_in_alembic_config(alembic_config, db_name: str, db_url: str, log):
    """Utility function, for internal use. Modify an alembic config object,
    adds a database, set the right url for this database. This makes sure the
    tests are run against databases which are not used by the server running
    outside on our systems."""
    before = alembic_config.get_main_option("databases")
    db_list = before.split(",")
    if before == "":
        db_list = []
    if db_name in db_list:
        raise Exception(
            f"The database {db_name} is already in alembic config. Can't add it twice."
        )
    db_list.append(db_name)
    after = ",".join(db_list)
    log.info(
        f"After adding {db_name}, the list of databases is {db_list} leading to {after}"
    )
    alembic_config.set_main_option("databases", after)
    alembic_config.set_section_option(db_name, "sqlalchemy.url", db_url)


def remove_db_from_alembic_config(alembic_config, db_name: str, log):
    """Utility function, for internal use. Removes a database that was previously
    added into the alembic config."""
    before = alembic_config.get_main_option("databases")
    db_list = before.split(",")
    if before == "":
        db_list = []
    if db_name not in db_list:
        raise Exception(
            f"The database {db_name} is not in alembic config. Can't remove it twice."
        )
    db_list = [x for x in db_list if x != db_name]
    after = ",".join(db_list)
    log.info(
        f"After removing {db_name}, the list of databases is {db_list} leading to {after}"
    )
    alembic_config.set_main_option("databases", after)


@pytest.fixture(scope="session")
def db_api_url(root_db, alembic_config, log) -> typing.Generator:
    """Fixture that makes a database available as the API db for testing.
    Adds the database and the url in alembic config. Yields an url to
    connect to that db."""
    log.info("SETUP api database (drop and create)")
    url = make_db("test", root_db)
    add_db_in_alembic_config(alembic_config, "api", url, log)
    yield url
    remove_db_from_alembic_config(alembic_config, "api", log)
    drop_db("test", root_db)
    log.info("TEARDOWN api database (drop)")


@pytest.fixture(scope="session")
def db_dovecot_url(root_db, alembic_config, log) -> typing.Generator:
    """Fixture that makes a database available as the Dovecot db for testing.
    Adds the database and the url in alembic config. Yields an url to
    connect to that db."""
    log.info("SETUP dovecot database (drop and create)")
    url = make_db("test2", root_db)
    add_db_in_alembic_config(alembic_config, "dovecot", url, log)
    yield url
    remove_db_from_alembic_config(alembic_config, "dovecot", log)
    drop_db("test2", root_db)
    log.info("TEARDOWN dovecot database (drop)")


@pytest.fixture(scope="session")
def db_postfix_url(root_db, alembic_config, log) -> typing.Generator:
    """Fixtures that makes a database available as the Postfix db for testing.
    Adds the database and the url in alembic config. Yields an url to
    connect to that db."""
    log.info("SETUP postfix database (drop and create)")
    url = make_db("test3",root_db)
    add_db_in_alembic_config(alembic_config, "postfix", url, log)
    yield url
    remove_db_from_alembic_config(alembic_config, "postfix", log)
    drop_db("test3",root_db)
    log.info("TEARDOWN postfix database (drop)")


@pytest.fixture(scope="function")
def alembic_run(alembic_config, log) -> typing.Generator:
    """Fixture that makes sure alembic has run on all the registered
    databases."""
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
def db_api(alembic_run, db_api_url, log) -> typing.Generator:
    """Fixture that makes sure a database is registered and ready to
    be used as the API db during tests."""
    log.info("SETUP sql_api to use the testing db")
    sql_api.init_db(db_api_url)
    yield


@pytest.fixture(scope="function")
def db_dovecot(alembic_run, db_dovecot_url, log) -> typing.Generator:
    """Fixture that makes sure a database is registered and ready to
    be used as the Dovecot db during tests."""
    log.info("SETUP sql_dovecot to use the testing db")
    sql_dovecot.init_db(db_dovecot_url)
    yield


@pytest.fixture(scope="function")
def db_postfix(alembic_run, db_postfix_url, log) -> typing.Generator:
    """Fixture that makes sure a database is registered and ready to
    be used as the Dovecot db during tests."""
    log.info("SETUP sql_postfix to use the testing db")
    sql_postfix.init_db(db_postfix_url)
    yield


@pytest.fixture(scope="function")
def db_api_session(db_api, log) -> typing.Generator:
    """Fixture that makes a connection to the API database available."""
    log.info("SETUP sql_api orm session")
    maker = sql_api.get_maker()
    session = maker()
    try:
        yield session
    finally:
        log.info("TEARDOWN sql_api orm session")
        session.close()


@pytest.fixture(scope="function")
def db_dovecot_session(db_dovecot, log) -> typing.Generator:
    """Fixture that makes a connecion to the Dovecot database available."""
    log.info("SETUP sql_dovecot orm session")
    maker = sql_dovecot.get_maker()
    session = maker()
    try:
        yield session
    finally:
        log.info("TEARDOWN sql_dovecot orm session")
        session.close()


@pytest.fixture(scope="function")
def db_postfix_session(db_postfix, log) -> typing.Generator:
    """Fixture that makes a connecion to the Dovecot database available."""
    log.info("SETUP sql_postfix orm session")
    maker = sql_postfix.get_maker()
    session = maker()
    try:
        yield session
    finally:
        log.info("TEARDOWN sql_postfix orm session")
        session.close()


@pytest.fixture(scope="function")
def ox_cluster(log) -> typing.Generator:
    """Fixture that provides an empty OX cluster."""
    log.info("SETUP empty ox cluster")
    ox_cluster = oxcli.OxCluster()
    ox_cluster.purge()
    yield ox_cluster
    log.info("TEARDOWN ox cluster")
    ox_cluster.purge()

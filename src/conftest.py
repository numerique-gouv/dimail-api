import logging
import os
import time
import typing

import alembic.command
import alembic.config
import pytest
import sqlalchemy as sa
import testcontainers.mysql as tc
from python_on_whales import DockerClient
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs

from . import oxcli, sql_api, sql_dovecot, sql_postfix, config


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
    mariadb_host = conn.engine.url.host
    return f"mysql+pymysql://{user}:{password}@{mariadb_host}:{mariadb_port}/{name}"


def drop_db(name: str, conn: sa.Connection):
    """Utility function, for internal use. Drops a database."""
    conn.execute(sa.text(f"drop database if exists {name};"))


@pytest.fixture(scope="session", name="log")
def fix_logger(scope="session") -> typing.Generator:
    """Fixture making the logger available"""
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("docker").setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info("SETUP logger")
    yield logger
    logger.info("TEARDOWN logger")


@pytest.fixture(scope="session")
def root_db(log, mariadb_container, request) -> typing.Generator:
    """
    Fixtures that makes a connection to mariadb/mysql as root available.
    Look at .docker_compose.yml to see args when fixture `mariadb_container` is not false
    """
    root_url = "mysql+pymysql://root:toto@localhost:3306/mysql"
    if mariadb_container:
        root_url = mariadb_container.get_connection_url()
    log.info(f"CONNECTING as mysql root to {root_url}")
    root_db = sa.create_engine(root_url)
    conn = root_db.connect()
    yield conn
    conn.close()
    log.info("CLOSING root mysql connection")


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
    url = make_db("test3", root_db)
    add_db_in_alembic_config(alembic_config, "postfix", url, log)
    yield url
    remove_db_from_alembic_config(alembic_config, "postfix", log)
    drop_db("test3", root_db)
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
def ox_cluster(log, ox_container) -> typing.Generator:
    """Fixture that provides an empty OX cluster."""
    log.info(f"SETUP empty ox cluster")
    ox_cluster = oxcli.OxCluster()
    log.info(f"url de connexion ssh vers le cluster OX -> {ox_cluster.url()}")
    ox_cluster.purge()
    yield ox_cluster
    log.info("TEARDOWN ox cluster")
    ox_cluster.purge()


@pytest.fixture(scope='session')
def ox_container(log, request, dimail_test_network, mariadb_container, ox_container_image) -> DockerContainer | None:
    if not mariadb_container:  # a besoin que mariadb soit up pour installer ox
        return None
    ox = (DockerContainer(ox_container_image)
          .with_network(dimail_test_network)
          .with_network_aliases("dimail_ox")
          .with_bind_ports(22))

    log.info("SETUP OX CONTAINER")
    ox.start()
    delay = wait_for_logs(ox, "Starting ssh daemon")
    log.info(f"ox started in -> {delay}s")
    time.sleep(1)  # pour être sûr que le service ssh est up

    ox_ssh_url = f"ssh://root@{ox.get_container_host_ip()}:{ox.get_exposed_port(22)}"
    log.info(f"url de connexion ssh vers le cluster OX -> {ox_ssh_url}")
    config.settings.ox_ssh_url = ox_ssh_url

    def remove_container():
        log.info("TEARDOWN OX CONTAINER")
        ox.stop()

    request.addfinalizer(remove_container)
    return ox


@pytest.fixture(scope="session")
def mariadb_container(log, request, dimail_test_network) -> tc.MySqlContainer | None:
    """
    Fixtures qui démarre un conteneur MariaDB avec le user root si
    la variable d'environnement `DIMAIL_STARTS_TESTS_CONTAINERS` n'est pas fausse
    """
    if not dimail_test_network:
        return None

    mysql = (tc.MySqlContainer("mariadb:11.2", username="root", password="toto", dbname="mysql")
             # .with_name("mariadb")
             .with_bind_ports(3306)
             .with_network(dimail_test_network)
             .with_network_aliases("mariadb"))
    log.info("SETUP MARIADB CONTAINER")
    mysql.start()
    delay = wait_for_logs(mysql, "MariaDB init process done. Ready for start up.")
    log.info(f"MARIADB started in {delay}s")

    def remove_container():
        mysql.stop()
        log.info("TEARDOWN MARIADB CONTAINER")

    request.addfinalizer(remove_container)
    return mysql


@pytest.fixture(scope='session')
def ox_container_image(log, request) -> str | None:
    if not need_start_test_container():
        return None
    pyw = DockerClient(log_level="WARN")
    tag = "dimail-oxtest"
    log.info(f"[START] construction de l'image -> {tag}")
    pyw.build("../oxtest/", tags=tag)
    time.sleep(2)  # pour être sûr que le tag soit bien arrivé dans le registry
    log.info(f"[END] construction de l'image -> {tag}")
    return tag


@pytest.fixture(scope="session")
def dimail_test_network(log) -> typing.Generator:
    if not need_start_test_container():
        yield None
    with Network() as dimail_test_network:
        log.info(f"crée un réseau Docker -> {dimail_test_network}")
        yield dimail_test_network


def need_start_test_container() -> bool:
    return bool(os.environ.get("DIMAIL_STARTS_TESTS_CONTAINERS"))

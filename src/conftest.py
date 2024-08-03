import logging
import os
import pathlib
import subprocess
import time
import typing

import fastapi
import fastapi.testclient
import pytest
import python_on_whales as pyow
import sqlalchemy as sa
import testcontainers.core as tc_core
import testcontainers.mysql as tc_mysql

import alembic.command
import alembic.config

from . import config, dkcli, main, oxcli, sql_api, sql_dovecot, sql_postfix

def make_db(name: str, conn: sa.Connection) -> str:
    """Utility function, for internal use. Ensure a database, named 'name'
    is created and empty. 'conn' is a mariadb/mysql connection as root user"""
    if conn == "sqlite":
        if pathlib.Path(f"/tmp/{name}.db").is_file():
            pathlib.Path.unlink(f"/tmp/{name}.db")
        return f"sqlite:////tmp/{name}.db"
    return make_db_with_user(name, "test", "toto", conn)


def make_db_with_user(name: str, user: str, password: str, conn: sa.Connection) -> str:
    """Utility function, for internal use. Ensure a database, named 'name'
    is created and empty. 'conn' is a mariadb/mysql connection as root user"""
    conn.execute(sa.text(f"drop database if exists {name};"))
    conn.execute(sa.text(f"create database {name};"))
    conn.execute(
        sa.text(f"grant ALL on {name}.* to {user}@'%' identified by '{password}';")
    )
    mariadb_port = conn.engine.url.port
    mariadb_host = conn.engine.url.host
    return f"mysql+pymysql://{user}:{password}@{mariadb_host}:{mariadb_port}/{name}"


def drop_db(name: str, conn: sa.Connection):
    """Utility function, for internal use. Drops a database."""
    if conn == "sqlite":
        pathlib.Path.unlink(f"/tmp/{name}.db")
        return
    conn.execute(sa.text(f"drop database if exists {name};"))


@pytest.fixture(scope="session", name="log")
def fix_logger(scope="session") -> typing.Generator:
    """Fixture making the logger available"""
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("docker").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("testcontainers.core.container").setLevel(logging.WARNING)
    logging.getLogger("testcontainers.core.waiting_utils").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info("SETUP logger")
    use_containers = config.settings.test_containers
    if use_containers:
        logger.warning("Will be generating test containers")
    yield logger
    logger.info("TEARDOWN logger")


@pytest.fixture(scope="session", params=["sqlite", "mysql"])
def db_type(log, request) -> typing.Generator:
    db_type = request.param
    log.info(f"SETUP testing with db_type={db_type}")
    yield db_type
    log.info(f"TEARDOWN testing with db_type={db_type}")


@pytest.fixture(scope="session")
def root_db(log, db_type, root_db_url, request) -> typing.Generator:
    """
    Fixtures that makes a connection to mariadb/mysql as root available.
    """
    if db_type == "mysql":
        log.info(f"CONNECTING as mysql root to {root_db_url}")
        root_db = sa.create_engine(root_db_url)
        conn = root_db.connect()
        yield conn
        conn.close()
        log.info(f"CLOSING root mysql connection to {root_db_url}")
    else:
        yield "sqlite"


@pytest.fixture(scope="session")
def alembic_config(db_type, log) -> typing.Generator:
    """Fixtures that makes available the alambic config, for future use. The
    list of databases is made empty. Alembic is told not to do anything to
    the logger, so that we can have logs where we want them."""
    log.info("SETUP alembic config")
    if not os.path.exists("alembic.ini"):
        raise Exception("Je veux tourner dans src, avec mon fichier alembic.ini")
    cfg = None
    if db_type == "sqlite":
        cfg = {}
    else:
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
    if isinstance(alembic_config, dict):
        alembic_config[db_name]=db_url
        return
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
    if isinstance(alembic_config, dict):
        alembic_config.pop(db_name)
        return
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
def db_api_url(db_type, root_db, alembic_config, log) -> typing.Generator:
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
def db_dovecot_url(db_type, root_db, alembic_config, log) -> typing.Generator:
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
def db_postfix_url(db_type, root_db, alembic_config, log) -> typing.Generator:
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
def alembic_run(db_type, alembic_config, log) -> typing.Generator:
    """Fixture that makes sure alembic has run on all the registered
    databases."""
    log.info("SETUP with alembic (upgrade)")
    if db_type == "mysql":
        bases = alembic_config.get_main_option("databases")
        log.info(f" - Here are the databases : {bases}")
        alembic.command.upgrade(alembic_config, "head")
    yield
    for sess in sa.orm.session._sessions.values():
        if sess._close_state != sa.orm.session._SessionCloseState.CLOSED:
            caller = sess.info["caller"]
            file   = sess.info["file"]
            log.error(f"We have an UNCLOSED session in the orm: {sess}")
            log.error(f"   caller: {caller} @ {file}")
            assert "" == f"WE LOST A SESSION created by {caller} @ {file}"
    log.info("TEARDOWN with alembic (downgrade)")
    if db_type == "mysql":
        bases = alembic_config.get_main_option("databases")
        alembic.command.downgrade(alembic_config, "base")
        log.info(f" - Here are the databases : {bases}")


@pytest.fixture(scope="function")
def db_api(db_type, alembic_run, db_api_url, log) -> typing.Generator:
    """Fixture that makes sure a database is registered and ready to
    be used as the API db during tests."""
    log.info(f"SETUP sql_api to use the testing db (url={db_api_url})")
    engine = sql_api.init_db(db_api_url)
    if db_type == "sqlite":
        log.info("- sqlite database, creating the tables")
        sql_api.Api.metadata.create_all(engine)
    yield
    log.info(f"TEARDOWN sql_api on testing db (url={db_api_url})")
    if db_type == "sqlite":
        log.info("- sqlite database, removing the tables")
        sql_api.Api.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_dovecot(db_type, alembic_run, db_dovecot_url, log) -> typing.Generator:
    """Fixture that makes sure a database is registered and ready to
    be used as the Dovecot db during tests."""
    log.info(f"SETUP sql_dovecot to use the testing db (url={db_dovecot_url})")
    engine = sql_dovecot.init_db(db_dovecot_url)
    if db_type == "sqlite":
        log.info("- sqlite database, creating the tables")
        sql_dovecot.Dovecot.metadata.create_all(engine)
    yield
    log.info(f"TEARDOWN sql_dovecot on testing db (url={db_dovecot_url})")
    if db_type == "sqlite":
        log.info("- sqlite database, removing the tables")
        sql_dovecot.Dovecot.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_postfix(db_type, alembic_run, db_postfix_url, log) -> typing.Generator:
    """Fixture that makes sure a database is registered and ready to
    be used as the Dovecot db during tests."""
    log.info(f"SETUP sql_postfix to use the testing db (url={db_postfix_url})")
    engine = sql_postfix.init_db(db_postfix_url)
    if db_type == "sqlite":
        log.info("- sqlite database, creating the tables")
        sql_postfix.Postfix.metadata.create_all(engine)
    yield
    log.info(f"TEARDOWN sql_dovecot on testing db (url={db_postfix_url})")
    if db_type == "sqlite":
        log.info("- sqlite database, droping the tables")
        sql_postfix.Postfix.metadata.drop_all(engine)


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
def ox_cluster(log, ox_name) -> typing.Generator:
    """Fixture that provides an empty OX cluster."""
    log.info("SETUP empty ox cluster")
    oxcli.set_default_cluster(ox_name)
    ox_cluster = oxcli.OxCluster()
    log.info(f"url de connexion ssh vers le cluster OX -> {ox_cluster.url()}")
    ox_cluster.purge()
    yield ox_cluster
    log.info("TEARDOWN ox cluster")
    ox_cluster.purge()


def make_image(log, name: str) -> str:
    pyw = pyow.DockerClient(log_level="WARN")
    tag = f"dimail-{name}"
    log.info(f"[START] construction de l'image -> {tag}")
    pyw.build(f"../{name}/", tags=tag)
    time.sleep(2)  # pour être sûr que le tag soit bien arrivé dans le registry
    log.info(f"[END] construction de l'image -> {tag}")
    return tag


def create_ssh_key(name: str):
    return_code = subprocess.call(["/bin/sh", "../ssh_docker/add_ssh_key.sh", name])
    if return_code != 0:
        raise Exception("Impossible to create ssh key")

@pytest.fixture(scope="session")
def ox_container(log, dimail_test_network) -> tc_core.container.DockerContainer:
    if not config.settings.test_containers:
        yield None
        return

    create_ssh_key("oxtest")
    image = make_image(log,"oxtest")
    ox = (
        tc_core.container.DockerContainer(image)
        .with_network(dimail_test_network)
        .with_network_aliases("dimail_ox")
        .with_bind_ports(22)
    )
    yield ox

@pytest.fixture(scope="session")
def dk_container(log, dimail_test_network) -> tc_core.container.DockerContainer:
    if not config.settings.test_containers:
        yield None
        return

    create_ssh_key("dktest")
    image = make_image(log,"dktest")
    dk = (
        tc_core.container.DockerContainer(image)
        .with_network(dimail_test_network)
        .with_network_aliases("dimail_dk")
        .with_bind_ports(22)
    )
    yield dk

@pytest.fixture(scope="session")
def ox_type(log, db_type) -> typing.Generator:
    if db_type == "sqlite":
        yield "fake"
    else:
        yield "real"

@pytest.fixture(scope="session")
def dk_manager(log, ox_type, dk_container) -> typing.Generator:
    if ox_type == "fake":
        log.info("SETUP using fake DK manager")
        dkcli.init_dkim_manager("FAKE", [])
        yield "FAKE"
        log.info("TEARDOWN using fake DK manager")
        return
    if not config.settings.test_containers:
        # We user the DK manager as declared in main.py
        yield ""
        return

    dk_container.start()
    delay = tc_core.waiting_utils.wait_for_logs(dk_container, "Starting ssh daemon")
    log.info(f"dk started in -> {delay}s")
    time.sleep(1)  # pour être sûr que le service ssh est up

    dk_ssh_url = f"ssh://root@{dk_container.get_container_host_ip()}:{dk_container.get_exposed_port(22)}"
    dk_ssh_args = [
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-i",
        "/tmp/dimail_dktest_id_rsa",
    ]
    log.info(f"url de connexion ssh vers le manager DK -> {dk_ssh_url}")
    dkcli.init_dkim_manager(dk_ssh_url, dk_ssh_args)
    yield ""
    log.info("TEARDOWN DK CONTAINER")
    dk_container.stop()


@pytest.fixture(scope="session")
def ox_name(log, ox_type, ox_container, root_db_url) -> typing.Generator:
    """Fixture that yields the URL for ssh to connect to the OX cluster. Will
    make a new (virgin) OX container, or will connect to the already existing
    one in docker compose, according to the setting of
    `DIMAIL_TEST_CONTAINERS`."""
    if ox_type == "fake":
        log.info("SETUP using fake OX cluster")
        oxcli.declare_cluster("FAKE", "FAKE", [])
        yield "FAKE"
        log.info("TEARDOWN using fake OX cluster")
        return
    if not config.settings.test_containers:
        # We use the OX cluster as declared in main.py
        yield "default"
        # We don't want to build a container as the teardown of the fixture.
        return

    log.info("SETUP OX CONTAINER")
    ox_container.start()
    delay = tc_core.waiting_utils.wait_for_logs(ox_container, "Starting ssh daemon")
    log.info(f"ox started in -> {delay}s")
    time.sleep(1)  # pour être sûr que le service ssh est up

    ox_ssh_url = f"ssh://root@{ox_container.get_container_host_ip()}:{ox_container.get_exposed_port(22)}"
    # on ne veut pas vérifier la clé sur chaque port randon du conteneur
    # et utilisation de la clé ssh générée par le script
    ox_ssh_args = [
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-i",
        "/tmp/dimail_oxtest_id_rsa",
    ]
    log.info(f"url de connexion ssh vers le cluster OX -> {ox_ssh_url}")

    oxcli.declare_cluster("testing", ox_ssh_url, ox_ssh_args)
    yield "testing"

    log.info("TEARDOWN OX CONTAINER")
    ox_container.stop()


@pytest.fixture(scope="session")
def root_db_url(log, dimail_test_network) -> tc_mysql.MySqlContainer | None:
    """Fixture that yields an URL to connect to the root database. The database
    will be running either in a dedicated container, or in your local docker
    compose, according to the settings `DIMAIL_TEST_CONTAINERS`."""
    if not config.settings.test_containers:
        yield "mysql+pymysql://root:toto@localhost:3306/mysql"
        return

    mariadb = (
        tc_mysql.MySqlContainer(
            "mariadb:11.2", username="root", password="toto", dbname="mysql"
        )
        # .with_name("mariadb")
        .with_bind_ports(3306)
        .with_network(dimail_test_network)
        .with_network_aliases("mariadb")
    )
    log.info("SETUP MARIADB CONTAINER")
    mariadb.start()
    delay = tc_core.waiting_utils.wait_for_logs(
        mariadb, "MariaDB init process done. Ready for start up."
    )
    log.info(f"MARIADB started in {delay}s")

    root_url = mariadb.get_connection_url()
    yield root_url

    mariadb.stop()
    log.info("TEARDOWN MARIADB CONTAINER")


@pytest.fixture(scope="session")
def dimail_test_network(log) -> typing.Generator:
    if not config.settings.test_containers:
        yield None
        return

    with tc_core.network.Network() as dimail_test_network:
        log.info("SETUP network for containers")
        log.info(f"crée un réseau Docker -> {dimail_test_network}")
        try:
            yield dimail_test_network
        finally:
            log.info("TEARDOWN network for containers")


@pytest.fixture(scope="session", name="client")
def get_api_client(log, scope="session") -> typing.Generator:
    """Fixture to get the API client"""
    log.info("SETUP the api client")
    client = fastapi.testclient.TestClient(main.app)
    yield client
    log.info("TEARDOWN the api client")


@pytest.fixture(scope="function", name="admin")
def first_admin_user(db_api, log, client):
    # Database is empty, fake auth, creating the first admin
    user = "admin"
    password = "admin"
    res = client.post(
        "/users/",
        json={"name": user, "password": password, "is_admin": True},
        auth=("useless", "useless"),
    )
    assert res.status_code == fastapi.status.HTTP_201_CREATED

    log.info("SETUP admin api user")
    yield {"user": user, "password": password}
    log.info("TEARDOWN admin api user")

def _make_user(log, client, admin, login, password):
    log.info(f"- creating the user {login}")
    res = client.post(
        "/users/",
        json={"name": login, "password": password, "is_admin": False},
        auth=(admin["user"], admin["password"]),
    )
    assert res.status_code == fastapi.status.HTTP_201_CREATED

    log.info(f"- creating a token for user {login}")
    res = client.get("/token/", auth=(login, password))
    assert res.status_code == 200
    token = res.json()["access_token"]

    return token


@pytest.fixture(scope="function")
def admin_token(log, client, admin):
    log.info("SETUP admin user with token")
    res = client.get("/token/", auth=(admin["user"], admin["password"]))
    assert res.status_code == 200
    token = res.json()["access_token"]
    yield {**admin, "token": token}

    log.info("TEARDOWN admin user with token")

@pytest.fixture(scope="function")
def virgin_user(log, client, admin, request):
    login, password = request.param.split(":",1)

    log.info(f"SETUP api user {login} (with no permissions)")
    token = _make_user(log, client, admin, login, password)
    yield {"user": login, "token": token}

    log.info(f"TEARDOWN api user {login}")


@pytest.fixture(scope="function")
def normal_user(log, client, admin, request):
    login, password = request.param.split(':',1)

    log.info(f"SETUP api user {login}")
    token = _make_user(log, client, admin, login, password)

    yield {"user": login, "token": token, "password": password}
    log.info(f"TEARDOWN api user {login}")

def _make_domain(
    log, client, admin,
    name: str,
    features: list[str],
    user: str | None = None,
    context_name: str = "useless",
):

    log.info("- creating the domain")
    res = client.post(
        "/domains/",
        params = {
            "no_check": "true",
        },
        json = {
            "name": name,
            "features": features,
            "context_name": context_name,
        },
        auth = (admin["user"], admin["password"]),
    )
    assert res.status_code == fastapi.status.HTTP_201_CREATED

    if user is not None:
        res = client.post(
            "/allows/",
            json={"user": user, "domain": name},
            auth=(admin["user"], admin["password"]),
        )
        assert res.status_code == fastapi.status.HTTP_201_CREATED

@pytest.fixture(scope="function")
def domain(log, client, admin, request):
    name = request.param
    features = []

    log.info(f"SETUP domain {name}, no features, no allowed users")
    _make_domain(log, client, admin, name, features, None)

    yield {"name": name, "features": features}
    log.info(f"TEARDOWN domain {name}")

# Syntaxe du param: les noms des domaines séparés par une virgule
# Ex: toto.fr,machin.com,truc.net
@pytest.fixture(scope="function")
def domain_mail(log, client, admin, normal_user, request):
    names = request.param.split(",")
    login = normal_user["user"]
    features = ["mailbox"]

    if len(names) > 1:
        log.info(f"SETUP domains {names}, allowed for user {login}, features: mailbox only")
    else:
        log.info(f"SETUP domain {names[0]}, allowed for user {login}, features: mailbox only")
    for name in names:
        _make_domain(log, client, admin, name, features, login)

    yield {"name": names[0], "features": features, "all_domains": names}
    if len(names) > 1:
        log.info(f"TEARDOWN domain {names}")
    else:
        log.info(f"TEARDOWN domain {names[0]}")

# Syntaxe du param: les noms de domaines séparés par une virgule, les
# différents contextes séparés par un point-virgule.
# Ex: toto.fr,toto.net:dimail;machin.com:ctx2
@pytest.fixture(scope="function")
def domain_web(log, client, admin, normal_user, ox_cluster, request):
    contexts = request.param.split(";")
    login = normal_user["user"]
    features = ["mailbox", "webmail"]

    all_domains = []
    all_contexts = []
    ctx_by_domain = {}
    domains_by_ctx = {}

    log.info(f"SETUP webmail domains, allowed for user {login}, features {features}")
    for ctx_info in contexts:
        domains, context_name = ctx_info.split(":",1)
        names = domains.split(",")

        all_contexts.append(context_name)
        domains_by_ctx[context_name] = []
        for name in names:
            log.info(f"- create domain {name}")
            all_domains.append(name)
            domains_by_ctx[context_name].append(name)
            ctx_by_domain[name] = context_name
            _make_domain(log, client, admin, name, features, login, context_name)
            log.info(f"- check the domain {name} is declared in the context {context_name}")
            ctx = ox_cluster.get_context_by_name(context_name)
            if ctx is None:
                exit(1)
            assert name in ctx.domains

    yield {
        "name": all_domains[0],
        "features": features,
        "context_name": all_contexts[0],
        "all_domains": all_domains,
        "all_contexts": all_contexts,
        "ctx_by_domain": ctx_by_domain,
        "domains_by_ctx": domains_by_ctx,
    }
    log.info(f"TEARDOWN web domains {all_domains}")


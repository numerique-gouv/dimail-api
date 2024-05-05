from typing import Generator
import logging
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import alembic.config
import alembic.command


@pytest.fixture(scope="session", name='log')
def fix_logger(scope="session") -> Generator:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info("SETUP logger")
    yield logger
    logger.info("TEARDOWN logger")

@pytest.fixture(scope="session")
def ensure_db(log) -> Generator:
    log.info("SETUP database (drop and create)")
    root_db = create_engine('mysql+pymysql://root:toto@localhost:3306/mysql')
    conn = root_db.connect()
    conn.execute(text("drop database if exists test;"))
    conn.execute(text("drop database if exists test2;"))
    conn.execute(text("create database test;"))
    conn.execute(text("create database test2;"))
    conn.execute(text("grant ALL on test.* to test@'%' identified by 'toto';"))
    conn.execute(text("grant ALL on test2.* to test@'%' identified by 'toto';"))
    yield 
    conn.execute(text("drop database if exists test;"))
    conn.execute(text("drop database if exists test2;"))
    conn.close()
    log.info("TEARDOWN database (drop)")

@pytest.fixture(scope="session")
def alembic_config(log) -> Generator:
    log.info("SETUP alembic config")
    cfg = alembic.config.Config("alembic.ini")
    cfg.set_main_option("init_logger", "False")
    cfg.set_main_option("script_location", "alembic")
    cfg.set_section_option("api", "sqlalchemy.url", 'mysql+pymysql://test:toto@localhost:3306/test')
    cfg.set_section_option("dovecot", "sqlalchemy.url", 'mysql+pymysql://test:toto@localhost:3306/test2')
    yield cfg
    log.info("TEARDOWN alembic config")

@pytest.fixture(scope="function")
def alembic_run(alembic_config, ensure_db, log) -> Generator:
    log.info("SETUP with alembic (upgrade)")
    alembic.command.upgrade(alembic_config, "head")
    yield 
    alembic.command.downgrade(alembic_config, "base")
    log.info("TEARDOWN with alembic (downgrade)")

@pytest.fixture(scope="function")
def db(alembic_run, log) -> Generator:
    log.info("SETUP orm session")
    test_db = create_engine('mysql+pymysql://test:toto@localhost:3306/test')
    Maker   = sessionmaker(autocommit=False, autoflush=False, autobegin=True, bind=test_db)
    session = Maker()
    yield session
    session.close()
    log.info("TEARDOWN session")



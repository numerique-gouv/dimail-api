import logging
import sqlalchemy
import sqlalchemy.orm as orm

from .. import config

url: str
engine: sqlalchemy.Engine
maker: orm.sessionmaker | None = None
db: orm.Session | None = None

Api = orm.declarative_base()

test = config.settings.api_db_url
import atexit

def close_db(db):
    db.close()

def init_api_db(config: str):
    global url
    global engine
    global maker
    url = config
    engine = sqlalchemy.create_engine(url)
    maker = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_api_db():
    global db
    global maker
    if db is None:
        if maker is None:
            raise Exception("You need to init the db by giving me a valid URL")
        db = maker()
        atexit.register(lambda: close_db(db))
    return db

def get_maker():
    global maker
    if maker is None:
        raise Exception("You need to init the db by giving me a valid URL")
    return maker

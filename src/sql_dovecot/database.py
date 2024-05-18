import typing

import sqlalchemy
import sqlalchemy.orm as orm

url: str
engine: sqlalchemy.Engine
maker: orm.sessionmaker | None = None
db: orm.Session

Dovecot = sqlalchemy.orm.declarative_base()

def close_db(db):
    db.close()

def init_dovecot_db(config: str):
    global url
    global engine
    global maker
    url = config
    engine = sqlalchemy.create_engine(url)
    maker = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_maker() -> orm.sessionmaker:
    global maker
    if maker is None:
        raise Exception("Please init the database by giving me an url...")
    return maker

def get_dovecot_db() -> orm.Session:
    global db
    global maker
    if db is None:
        if maker is None:
            raise Exception("Please init the database by giving me an url...")
        db = maker()
        atexit.register(lambda: close_db(db))
    return db


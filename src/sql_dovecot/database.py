import inspect
import atexit

import sqlalchemy as sa
import sqlalchemy.orm as orm

# url: str
# engine: sa.Engine
maker: orm.sessionmaker | None = None
db: orm.Session

Dovecot = orm.declarative_base()


def close_db(db):
    db.close()


def init_db(config: str):
    # global url
    # global engine
    global maker
    url = config
    engine = sa.create_engine(url)
    maker = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine, info={}, close_resets_only=False)

def get_maker() -> orm.sessionmaker:
    global maker
    if maker is None:
        raise Exception("Please init the database by giving me an url...")
    caller = inspect.currentframe().f_back.f_code.co_qualname
    file = inspect.currentframe().f_back.f_code.co_filename
    line = inspect.currentframe().f_back.f_code.co_firstlineno
    maker.kw["info"]["caller"] = caller
    maker.kw["info"]["file"] = f"{file}:{line}"
    return maker


def get_db() -> orm.Session:
    global db
    global maker
    raise Exception("Deprecated")
    if db is None:
        if maker is None:
            raise Exception("Please init the database by giving me an url...")
        db = maker()
        atexit.register(lambda: close_db(db))
    return db

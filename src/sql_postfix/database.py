import atexit
import inspect

import sqlalchemy as sa
import sqlalchemy.orm as orm

maker: orm.sessionmaker | None = None
db: orm.Session

Postfix = orm.declarative_base()


def close_db(db):
    db.close()


def init_db(config: str):
    global maker
    url = config
    engine = sa.create_engine(url)
    maker = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine, info={"key": "Benjamin"}, close_resets_only=False)

def get_maker() -> orm.sessionmaker:
    global maker
    if maker is None:
        raise Exception("Please init the postfix database by giving me an url...")
    caller = inspect.currentframe().f_back.f_code.co_qualname
    file = inspect.currentframe().f_back.f_code.co_filename
    line = inspect.currentframe().f_back.f_code.co_firstlineno
    maker.kw["info"]["key"] = "Lautre"
    maker.kw["info"]["caller"] = caller
    maker.kw["info"]["file"] = f"{file}:{line}"
    return maker


def get_db() -> orm.Session:
    global db
    if db is None:
        maker = get_maker()
        db = maker()
        atexit.register(lambda: db.close())
    return db

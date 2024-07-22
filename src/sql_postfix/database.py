import inspect

import sqlalchemy as sa
import sqlalchemy.orm as orm

maker: orm.sessionmaker | None = None

Postfix = orm.declarative_base()


def init_db(config: str):
    global maker
    url = config
    engine = sa.create_engine(url)
    maker = orm.sessionmaker(autocommit=False,
                             autoflush=False,
                             bind=engine,
                             info={},
                             close_resets_only=False)
    return engine


def get_maker() -> orm.sessionmaker:
    global maker
    if maker is None:
        raise Exception("Please init the postfix database by giving me an url...")
    caller = inspect.currentframe().f_back.f_code.co_qualname
    file = inspect.currentframe().f_back.f_code.co_filename
    line = inspect.currentframe().f_back.f_code.co_firstlineno
    maker.kw["info"]["caller"] = caller
    maker.kw["info"]["file"] = f"{file}:{line}"
    return maker


import inspect

import sqlalchemy as sa
import sqlalchemy.orm as orm

maker: orm.sessionmaker | None = None

Api = orm.declarative_base()


def init_db(config: str):
    global maker
    url = config
    engine = sa.create_engine(url)
    maker = orm.sessionmaker(autocommit=False,
                             autoflush=False,
                             bind=engine,
                             info={},
                             close_resets_only=False)


def get_maker():
    global maker
    if maker is None:
        raise Exception("You need to init the db by giving me a valid URL")
    caller = inspect.currentframe().f_back.f_code.co_qualname
    file = inspect.currentframe().f_back.f_code.co_filename
    line = inspect.currentframe().f_back.f_code.co_firstlineno
    maker.kw["info"]["caller"] = caller
    maker.kw["info"]["file"] = f"{file}:{line}"
    return maker

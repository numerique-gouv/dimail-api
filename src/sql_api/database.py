import inspect

import sqlalchemy as sa
import sqlalchemy.orm as orm

maker: orm.sessionmaker | None = None

Api = orm.declarative_base()

class DbApi:
    maker: orm.sessionmaker
    def __init__(self, config: str):
        self.url = config
        if config == "FAKE":
            return
        self.engine = sa.create_engine(url)
        self.maker = orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            info={},
            close_resets_only=False,
        )
    def get_maker(self) -> orm.sessionmaker:
        if self.maker is None:
            raise Exception("You need to init the db by giving me a valid URL")
        caller = inspect.currentframe().f_back.f_code.co_qualname
        file = inspect.currentframe().f_back.f_code.co_filename
        line = inspect.currentframe().f_back.f_code.co_firstlineno
        maker.kw["info"]["caller"] = caller
        maker.kw["info"]["file"] = f"{file}:{line}"
        return maker



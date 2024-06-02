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
    maker = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_maker() -> orm.sessionmaker:
    global maker
    if maker is None:
        raise Exception("Please init the postfix database by giving me an url...")
    return maker


def get_db() -> orm.Session:
    global db
    if db is None:
        maker = get_maker()
        db = maker()
        atexit.register(lambda: db.close())
    return db

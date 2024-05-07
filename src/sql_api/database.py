import sqlalchemy
import sqlalchemy.orm

url: str
engine: sqlalchemy.Engine
maker: sqlalchemy.orm.sessionmaker | None = None

Api = sqlalchemy.orm.declarative_base()

def init_api_db(config: str):
    global url
    global engine
    global maker
    url = config
    engine = sqlalchemy.create_engine(url)
    maker = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_api_db():
    global maker
    if maker is None:
        raise Exception("We need to init the database")
    db = maker()
    try:
        yield db
    finally:
        db.close()

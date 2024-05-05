from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

IMAP_DB='mysql+pymysql://dovecot:toto@localhost:3306/toto'

engine = create_engine(
  IMAP_DB
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Dovecot = declarative_base()


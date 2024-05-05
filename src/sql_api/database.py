from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

API_DB='mysql+pymysql://api_user:coincoin@localhost:3306/api'

api_db = create_engine(API_DB)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=api_db)

Api = declarative_base()

def get_api_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


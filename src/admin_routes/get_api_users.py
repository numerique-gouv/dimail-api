from fastapi import Depends
from sql_api import database, schemas, crud
from . import ox

@ox.get(
  '/api/users'
)
async def get_api_users(
  db = Depends(database.get_api_db),
) -> list[schemas.ApiUser]:
  users = crud.get_api_users(db)
  return users


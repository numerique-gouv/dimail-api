from src.models import User
from . import users

#@users.get("/{user_id}", response_model=User)
#async def get_user(user_id: int, user: User):
#    return {"user_id": str(user_id), "user_email": "marie@mail.fr"}

from fastapi import Depends, HTTPException
import src.sql_api


@users.get(
  '/{user_name}'
)
async def get_user(
  user_name: str,
  db = Depends(src.sql_api.get_api_db)
) -> src.sql_api.WApiUser:
  user_db = src.sql_api.get_api_user(db, user_name)
  if user_db is None:
    raise HTTPException(status_code=404, detail='User not found')
  return user_db



import fastapi

from .. import sql_api
from . import users

@users.get("/{user_name}")
async def get_user(
    user_name: str,
    db=fastapi.Depends(sql_api.get_api_db)
) -> sql_api.WApiUser:
    user_db = sql_api.get_api_user(db, user_name)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    return user_db

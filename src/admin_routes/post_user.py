import fastapi

from .. import sql_api
from . import users


@users.post("/")
async def post_user(
    user: sql_api.WApiUser,
    db=fastapi.Depends(sql_api.get_api_db),
) -> sql_api.WApiUser:
    user_db = sql_api.get_api_user(db, user.name)
    if user_db is not None:
        raise fastapi.HTTPException(status_code=409, detail="User already exists")
    return sql_api.create_api_user(db, user)

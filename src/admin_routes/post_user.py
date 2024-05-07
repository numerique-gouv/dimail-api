from fastapi import Depends, HTTPException

import src.sql_api

from . import users


@users.post("/")
async def post_user(
    user: src.sql_api.WApiUser,
    db=Depends(src.sql_api.get_api_db),
) -> src.sql_api.WApiUser:
    user_db = src.sql_api.get_api_user(db, user.name)
    if user_db is not None:
        raise HTTPException(status_code=409, detail="User already exists")
    return src.sql_api.create_api_user(db, user)

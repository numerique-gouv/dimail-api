from fastapi import Depends

import src.sql_api

from . import users


@users.get("/")
async def get_users(
    db=Depends(src.sql_api.get_api_db),
) -> list[src.sql_api.WApiUser]:
    users = src.sql_api.get_api_users(db)
    return users

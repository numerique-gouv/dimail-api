import fastapi

from .. import sql_api, web_models
from . import depends_api_db, users


@users.get("/{user_name}")
async def get_user(
    user_name: str, db=fastapi.Depends(depends_api_db)
) -> web_models.WUser:
    user_db = sql_api.get_api_user(db, user_name)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    return user_db

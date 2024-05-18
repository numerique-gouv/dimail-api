import fastapi

from .. import sql_api, web_models
from . import depends_api_db, users


@users.post("/")
async def post_user(
    user: web_models.CreateUser,
    db=fastapi.Depends(depends_api_db),
) -> web_models.WUser:
    user_db = sql_api.get_api_user(db, user.name)

    if user_db is not None:
        raise fastapi.HTTPException(status_code=409, detail="User already exists")

    return sql_api.create_api_user(
        db, name=user.name, password=user.password, is_admin=user.is_admin
    )

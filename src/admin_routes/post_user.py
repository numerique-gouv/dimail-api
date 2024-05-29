import fastapi

from .. import auth, sql_api, web_models
from . import DependsApiDb, users


@users.post("/", status_code=201)
async def post_user(
    db: DependsApiDb,
    admin: auth.DependsBasicAdmin,
    user: web_models.CreateUser,
) -> web_models.WUser:
    """Create user."""

    user_db = sql_api.get_user(db, user.name)

    if user_db is not None:
        raise fastapi.HTTPException(status_code=409, detail="User already exists")

    return sql_api.create_api_user(
        db, name=user.name, password=user.password, is_admin=user.is_admin
    )

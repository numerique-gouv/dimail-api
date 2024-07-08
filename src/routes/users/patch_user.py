import fastapi

from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.users.patch("/{user}", status_code=200)
async def patch_user(
    user: str,
    db: dependencies.DependsApiDb,
    admin: auth.DependsBasicAdmin,
    updates: web_models.UpdateUser,
) -> web_models.User:
    """Updates a user."""

    user_db = sql_api.get_user(db, user)

    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="Not found")

    if updates.password is not None:
        user_db = sql_api.update_user_password(db, user, updates.password)

    if updates.is_admin is not None:
        user_db = sql_api.update_user_is_admin(db, user, updates.is_admin)

    return web_models.User.from_db(user_db)

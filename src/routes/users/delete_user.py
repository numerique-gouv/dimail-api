import fastapi

from ... import auth, sql_api
from .. import dependencies, routers


@routers.users.delete("/{user_name}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    user_name: str,
) -> None:
    user_db = sql_api.get_user(db, user_name)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="Not found")

    sql_api.delete_allows_by_user(db, user_name)
    sql_api.delete_user(db, user_name)
    return None


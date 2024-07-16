import fastapi

from ... import auth, sql_api
from .. import dependencies, routers


@routers.users.delete("/{user_name}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    user_name: str,
) -> None:
    """Delete a user by name.

    To delete a user, you must be an admin user.

    Args:
        db (dependencies.DependsApiDb): Database session
        user (auth.DependsBasicAdmin): User credentials
        user_name (str): User name

    Returns:
        None: No content

    Raises:
        fastapi.HTTPException: Not found

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsBasicAdmin
        dependencies.DependsApiDb
        routers
        sql_api.delete_allows_by_user
        sql_api.delete_user
        sql_api.get_user
    """
    user_db = sql_api.get_user(db, user_name)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="Not found")

    sql_api.delete_allows_by_user(db, user_name)
    sql_api.delete_user(db, user_name)
    return None


from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.allows.get(
    "/",
    response_model=list[web_models.Allowed],
    responses={
        200: {"description": "Allows"},
    },
    status_code=200,
    description="Get all allows",
)
async def get_allows(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    username: str = "",
    domain: str = "",
) -> list[web_models.Allowed]:
    """Get all allows in a domain.

    To get all allows in a domain, you must be an admin user.

    Args:
        db (dependencies.DependsApiDb): Database session
        user (auth.DependsBasicAdmin): User credentials
        username (str): User name
        domain (str): Domain name

    Returns:
        list[web_models.Allowed]: List of allows

    Raises:
        No raises.

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsBasicAdmin
        dependencies.DependsApiDb
        sql_api.get_allows
        web_models.Allowed.from_db
    """
    allows = sql_api.get_allows(db, username, domain)
    return [web_models.Allowed.from_db(allow) for allow in allows]

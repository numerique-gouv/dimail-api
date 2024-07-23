import fastapi

from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.allows.post(
    "/",
    status_code=201,
    response_model=web_models.Allowed,
    responses={
        201: {"description": "Allow created"},
        403: {"description": "Permission denied"},
        404: {"description": "Domain not found"},
        409: {"description": "Domain already allowed for this user"},
    },
    description="Give allows of a domain to a user",
)
async def post_allow(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    allow: web_models.Allowed,
) -> web_models.Allowed:
    """Give ownership of a domain to a user.

    To give ownership of a domain to a user, you must be an admin user.

    Args:
        db (dependencies.DependsApiDb): Database session
        user (auth.DependsBasicAdmin): User credentials
        allow (web_models.Allowed): Allow information

    Returns:
        web_models.Allowed: Allowed information

    Raises:
        fastapi.HTTPException: Domain not found
        fastapi.HTTPException: User not found
        fastapi.HTTPException: Domain already allowed for this user

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsBasicAdmin
        dependencies.DependsApiDb
        routers
        sql_api.allow_domain_for_user
        sql_api.get_allowed
        sql_api.get_domain
        sql_api.get_user
        web_models.Allowed.from_db
    """

    user_db = sql_api.get_user(db, allow.user)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")

    domain_db = sql_api.get_domain(db, allow.domain)
    if domain_db is None:
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    allowed_db = sql_api.get_allowed(db, allow.user, allow.domain)
    if allowed_db is not None:
        raise fastapi.HTTPException(
            status_code=409, detail="Domain already allowed for this user"
        )

    allowed_db = sql_api.allow_domain_for_user(db, user=allow.user, domain=allow.domain)
    return web_models.Allowed.from_db(allowed_db)

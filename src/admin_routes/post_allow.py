import fastapi

from .. import auth, sql_api, web_models
from . import DependsApiDb, allows


@allows.post("/", status_code=201)
async def post_allow(
    db: DependsApiDb,
    user: auth.DependsBasicAdmin,
    allow: web_models.WAllowed,
) -> web_models.WAllowed:
    """Give ownership of a domain to a user."""

    user_db = sql_api.get_api_user(db, allow.user)

    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    domain_db = sql_api.get_api_domain(db, allow.domain)
    if domain_db is None:
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")
    allowed_db = sql_api.get_api_allowed(db, allow.user, allow.domain)
    if allowed_db is not None:
        raise fastapi.HTTPException(
            status_code=409, detail="Domain already allowed for this user"
        )
    return sql_api.allow_domain_for_user(db, allow)

import fastapi

from ... import auth, sql_api
from .. import dependencies, routers


@routers.allows.delete("/{domain_name}/{user_name}", status_code=204)
async def delete_allow(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    domain_name: str,
    user_name: str,
) -> None:
    """Remove user ownership of a domain."""

    user_db = sql_api.get_user(db, user_name)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")

    domain_db = sql_api.get_domain(db, domain_name)
    if domain_db is None:
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    allowed_db = sql_api.get_allowed(db, user_name, domain_name)
    if allowed_db is None:
        raise fastapi.HTTPException(
            status_code=404,
            detail="Queried user does not have permissions for this domain.",
        )

    return sql_api.deny_domain_for_user(db, user=user_name, domain=domain_name)

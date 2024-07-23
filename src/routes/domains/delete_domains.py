import fastapi

from ... import auth, config, sql_api
from .. import dependencies, routers

@routers.domains.delete(
    "/{domain_name}",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    summary="Delete a domain",
    description="Delete a domain and all its data",
    response_model=None,
)
def delete_domain(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    domain_name: str,
):
    """Delete a domain by name.

    To delete a domain, you must be an admin user.
    To delete we need to remove all data related to the domain.
        - mailboxes
        - aliases
        - subdomains
        - domain itself
    If the domain has a webmail feature, we need to remove the context from OX.
    To remove the context from OX, we need to remove all mailboxes and aliases from the context.
        - ox users
        - aliases
        - calendars
        - contacts
        - tasks
        - folders
        - settings
        - context itself (if no more domains are mapped to it)

    Args:
        db (dependencies.DependsApiDb): Database session
        user (auth.DependsBasicAdmin): User credentials
        domain_name (str): Domain name

    Returns:
        None: No content

    Raises:
        fastapi.HTTPException: Domain not found
        fastapi.HTTPException: Not implemented

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        dependencies.DependsApiDb
        routers
        sql_api.delete_domain
        sql_api.get_domain
        web_models
    """
    if not config.debug:
        raise fastapi.HTTPException(status_code=501, detail="Not implemented")
    domain_db = sql_api.get_domain(db, domain_name)
    if domain_db is None:
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    sql_api.delete_domain(db, domain_name)
    return None

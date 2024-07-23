import logging

import fastapi

from ... import auth, sql_postfix
from .. import dependencies, routers


@routers.aliases.delete(
    "/{user_name}/{destination}",
    description="Deletes an alias. "
        "When destination=all, will remove all the destinations.",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_alias(
    domain_name: str,
    user_name: str,
    destination: str,
    user: auth.DependsTokenUser,
    db: dependencies.DependsPostfixDb,
) -> None:
    """Delete an alias by name.

    To delete an alias, you must be an admin user.

    Args:
        domain_name (str): Domain name
        user_name (str): User name
        destination (str): Destination name
        user (auth.DependsTokenUser): User credentials
        db (dependencies.DependsPostfixDb): Database session

    Returns:
        None: No content

    Raises:
        fastapi.HTTPException: Not found
        fastapi.HTTPException: Permission denied

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsTokenUser
        dependencies.DependsPostfixDb
        sql_postfix.delete_alias
        sql_postfix.delete_aliases_by_name
    """
    log = logging.getLogger(__name__)

    perms = user.get_creds()
    if not perms.can_read(domain_name):
        log.info(f"Cet utilisateur n'a pas les droits sur le domaine {domain_name}")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    name = user_name + "@" + domain_name
    if destination == "all":
        log.info(f"On demande la suppression de toutes les destinations pour {name}")
        count = sql_postfix.delete_aliases_by_name(db, name)
        if count == 0:
            raise fastapi.HTTPException(status_code=404, detail="Not found")
        return None

    log.info("On supprime un alias exact")
    count = sql_postfix.delete_alias(db, name, destination)
    if count == 0:
        log.info("Cet alias n'existe pas")
        raise fastapi.HTTPException(status_code=404, detail="Not found")

    return None


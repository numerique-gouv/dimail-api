import logging

import fastapi

from ... import auth, sql_postfix
from .. import dependencies, routers


@routers.aliases.delete(
    "/{user_name}/{destination}",
    description="Deletes an alias. "
        "When destination=all, will remove all the destinations.",
    status_code=204
)
async def delete_alias(
    domain_name: str,
    user_name: str,
    destination: str,
    user: auth.DependsTokenUser,
    db: dependencies.DependsPostfixDb,
) -> None:
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


import logging

import fastapi

from .. import auth, sql_postfix, web_models
from . import DependsPostfixDb, aliases


@aliases.get("/", description="Gets an exact alias")
async def get_alias(
    domain: str,
    user: auth.DependsTokenUser,
    db: DependsPostfixDb,
    username: str = "",
    destination: str = "",
) -> list[web_models.Alias]:
    log = logging.getLogger(__name__)

    perms = user.get_creds()
    if not perms.can_read(domain):
        log.info(f"Cet utilisateur n'a pas les droits sur le domaine {domain}")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    if username == "" and destination == "":
        log.info(
            "Pas de username, pas de destination, on cherche tous les alias du domaine"
        )
        db_aliases = sql_postfix.get_aliases_by_domain(db, domain)
        return [web_models.Alias.from_db(x) for x in db_aliases]

    name = username + "@" + domain
    if destination == "":
        log.info(
            "Pas de destination, on cherche toutes les destinations pour une adresse mail"
        )
        db_aliases = sql_postfix.get_aliases_by_name(db, name)
        return [web_models.Alias.from_db(x) for x in db_aliases]

    log.info("On cherche un alias exact")
    db_alias = sql_postfix.get_alias(db, name, destination)
    if db_alias is None:
        log.info("Cet alias n'existe pas")
        raise fastapi.HTTPException(status_code=404, detail="Alias not found")

    return [web_models.Alias.from_db(db_alias)]

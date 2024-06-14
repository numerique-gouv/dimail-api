import logging

import fastapi

from .. import auth, sql_postfix, web_models
from .dependencies import DependsPostfixDb
from . import aliases


@aliases.post("/", description="Creates an alias in postfix")
async def post_alias(
    alias: web_models.Alias,
    user: auth.DependsTokenUser,
    db: DependsPostfixDb,
) -> web_models.Alias:
    log = logging.getLogger(__name__)

    perms = user.get_creds()
    if not perms.can_read(alias.domain):
        log.info(f"Cet utilisateur n'a pas les droits sur le domaine {alias.domain}")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    name = alias.username + "@" + alias.domain
    db_alias = sql_postfix.get_alias(db, name, alias.destination)
    if db_alias is not None:
        log.info("Cet alias existe deja")
        raise fastapi.HTTPException(status_code=409, detail="Alias already exists")

    db_alias = sql_postfix.create_alias(db, alias.domain, alias.username, alias.destination)

    return web_models.Alias.from_db(db_alias)

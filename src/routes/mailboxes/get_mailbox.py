import logging

import fastapi

from ... import auth, oxcli, sql_dovecot, web_models
from .. import dependencies, routers

# uuid_re = re.compile("^[0-9a-f-]{32,36}$")


@routers.mailboxes.get(
    "/{user_name}",
    responses={
        200: {"description": "Get a mailbox from their e-mail"},
        403: {"description": "Permission denied"},
        404: {"description": "Mailbox not found"},
        422: {"description": "Email address is not well formed"},
    },
    description="Fetch a mailbox <user_name> in domain <domain_name> (<user_name>@<domain_name>)",
)
async def get_mailbox(
    user_name: str,
    domain_name: str,
    user: auth.DependsTokenUser,
    db: dependencies.DependsDovecotDb,
    # alias_db: typing.Annotated[typing.Any, fastapi.Depends(sql_alias.get_alias_db)],
) -> web_models.Mailbox:
    log = logging.getLogger(__name__)
    email = f"{user_name}@{domain_name}"
    log.info(f"Nous cherchons qui est {email}")
    perms = user.get_creds()
    log.info(f"Nous avons comme permissions: {perms}")

    if not perms.can_read(domain_name):
        log.info(f"Permission denied on domain {domain_name} for current user")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    ox_cluster = oxcli.OxCluster()
    ctx = ox_cluster.get_context_by_domain(domain_name)

    if ctx is None:
        log.info("Aucun contexte ne gère le domaine chez OX")

    ox_user = None
    if ctx:
        ox_user = ctx.get_user_by_email(email)

    if ox_user is None:
        log.info("Le contexte OX ne connait pas cet email")

    db_user = sql_dovecot.get_user(db, user_name, domain_name)
    if db_user is None:
        log.info("La base dovecot ne contient pas cette adresse.")

    if db_user is None and ox_user is None:
        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    return web_models.Mailbox.from_both_users(ox_user, db_user)

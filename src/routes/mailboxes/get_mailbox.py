import logging

import fastapi

from ... import auth, oxcli, sql_api, sql_dovecot, web_models
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
    description="Fetch a mailbox user_name in domain domain_name (user_name@domain_name)",
    response_model=web_models.Mailbox,
)
async def get_mailbox(
    user_name: str,
    domain_name: str,
    user: auth.DependsTokenUser,
    imap: dependencies.DependsDovecotDb,
    api: dependencies.DependsApiDb,
    # alias_db: typing.Annotated[typing.Any, fastapi.Depends(sql_alias.get_alias_db)],
) -> web_models.Mailbox:
    """Get a mailbox by email address.

    Args:
        user_name (str): User name
        domain_name (str): Domain name
        user (auth.DependsTokenUser): User credentials
        imap (dependencies.DependsDovecotDb): Dovecot database session
        api (dependencies.DependsApiDb): API database session

    Returns:
        web_models.Mailbox: Mailbox information

    Raises:
        fastapi.HTTPException: Permission denied
        fastapi.HTTPException: Domain not found
        fastapi.HTTPException: Mailbox not found
        fastapi.HTTPException: Email address is not well formed

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsTokenUser
        dependencies.DependsApiDb
        dependencies.DependsDovecotDb
        oxcli
        sql_api.get_domain
        sql_dovecot.get_user
        web_models.Mailbox.from
    """
    log = logging.getLogger(__name__)
    email = f"{user_name}@{domain_name}"
    log.info(f"Nous cherchons qui est {email}")
    perms = user.get_creds()
    log.info(f"Nous avons comme permissions: {perms}")

    if not perms.can_read(domain_name):
        log.info(f"Permission denied on domain {domain_name} for current user")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    db_domain = sql_api.get_domain(api, domain_name)
    if db_domain is None:
        log.info(f"Le domaine {domain_name} n'existe pas dans la base API")
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    with_webmail = False
    if "webmail" in db_domain.features:
        with_webmail = True

    ox_cluster = oxcli.OxCluster()
    ctx = ox_cluster.get_context_by_domain(domain_name)

    if with_webmail and ctx is None:
        log.info("Aucun contexte ne gère le domaine chez OX (ce n'est pas normal)")
    if not with_webmail and ctx:
        log.info("Il y a un context pour ce domaine chez OX (ce n'est pas normal)")

    ox_user = None
    if ctx:
        ox_user = ctx.get_user_by_email(email)

    if with_webmail and ox_user is None:
        log.info("Le contexte OX ne connait pas cet email")
    if not with_webmail and ox_user:
        log.info("Le contexte OX connait cet email (ce n'est pas normal)")

    db_user = sql_dovecot.get_user(imap, user_name, domain_name)
    if db_user is None:
        log.info("La base dovecot ne contient pas cette adresse.")

    if db_user is None and ox_user is None:
        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    return web_models.Mailbox.from_both_users(ox_user, db_user, with_webmail)

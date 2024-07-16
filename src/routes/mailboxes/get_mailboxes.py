import logging

import fastapi

from ... import auth, oxcli, sql_api, sql_dovecot, web_models
from .. import dependencies, routers


@routers.mailboxes.get(
    "/",
    responses={
        200: {"description": "Get users from query request"},
        403: {"description": "Permission denied, insuficient permissions to perform the request"},
        404: {"description": "No users matched the query"},
    },
)
async def get_mailboxes(
    imap: dependencies.DependsDovecotDb,
    api: dependencies.DependsApiDb,
    user: auth.DependsTokenUser,
    domain_name: str,
    #  page_size: int = 20,
    #  page_number: int = 0,
):
    """Get all mailboxes in a domain.

    Args:
        domain_name (str): Domain name
        user (auth.DependsTokenUser): User credentials
        imap (dependencies.DependsDovecotDb): Dovecot database session
        api (dependencies.DependsApiDb): API database session

    Returns:
        list[web_models.Mailbox]: List of mailboxes

    Raises:
        fastapi.HTTPException: Permission denied
        fastapi.HTTPException: Domain not found

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
        sql_dovecot.get_users
        web_models.Mailbox.from_both_users
    """
    log = logging.getLogger(__name__)
    log.info(f"Searching mailboxes in domain {domain_name}\n")

    perms = user.get_creds()

    if not perms.can_read(domain_name):
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    db_domain = sql_api.get_domain(api, domain_name)
    if db_domain is None:
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    with_webmail = False
    if "webmail" in db_domain.features:
        with_webmail = True

    # Find the expected domain
    ox_cluster = oxcli.OxCluster()
    ctx = ox_cluster.get_context_by_domain(domain_name)
    if with_webmail and ctx is None:
        log.info(f"Le domaine {domain_name} est inconnu du cluster OX (ce n'est pas normal)")
    if not with_webmail and ctx:
        log.info(f"Le domaine {domain_name} est connu du cluster OX (ce n'est pas normal)")

    ox_users = []
    if ctx:
        ox_users = ctx.list_users()

    db_users = sql_dovecot.get_users(imap, domain_name)

    emails = set([user.email for user in ox_users] + [user.email() for user in db_users])
    ox_users_dict = {user.email: user for user in ox_users}
    db_users_dict = {user.email(): user for user in db_users}

    my_mailboxes = [
        web_models.Mailbox.from_both_users(
            ox_users_dict.get(email),
            db_users_dict.get(email),
            with_webmail,
        )
        for email in emails
    ]

    return my_mailboxes

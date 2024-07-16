import logging
import secrets
import uuid

import fastapi

from ... import auth, oxcli, sql_api, sql_dovecot, web_models
from .. import dependencies, routers


@routers.mailboxes.post(
    "/{user_name}",
    description="Create a mailbox in dovecot and OX",
    status_code=201,
)
async def post_mailbox(
    mailbox: web_models.CreateMailbox,
    user: auth.DependsTokenUser,
    db: dependencies.DependsDovecotDb,
    db_api: dependencies.DependsApiDb,
    user_name: str,
    domain_name: str,
) -> web_models.NewMailbox:
    """Create a mailbox in dovecot and OX.

    Args:
        mailbox (web_models.CreateMailbox): Mailbox information
        user (auth.DependsTokenUser): User credentials
        db (dependencies.DependsDovecotDb): Dovecot database session
        db_api (dependencies.DependsApiDb): API database session
        user_name (str): User name
        domain_name (str): Domain name

    Returns:
        web_models.NewMailbox: New mailbox information

    Raises:
        fastapi.HTTPException: Permission denied
        Exception: Domain not found in OX

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
        sql_dovecot.create_user
        web_models.CreateMailbox
        web_models.NewMailbox

    Exemples:
        * POST /domains/test.com/mailboxes/test.user
        import client

        client.post(
        "domains/test.com/mailboxes/test.user",
        json={"givenName": "Test", "surName": "User"},
        headers={"Authorization: Bearer token"}
        )
    """
    log = logging.getLogger(__name__)

    perms = user.get_creds()
    if not perms.can_read(domain_name):
        log.info(f"Cet utilisateur ne peut pas traiter le domaine {domain_name}")
        raise fastapi.HTTPException(status_code=403, detail="Permisison denied")

    domain = sql_api.get_domain(db_api, domain_name)
    if domain.has_feature(web_models.Feature.Webmail):
        ox_cluster = oxcli.OxCluster()
        ctx = ox_cluster.get_context_by_domain(domain_name)
        if ctx is None:
            log.error(f"Le domaine {domain_name} est inconnu du cluster OX")
            raise Exception("Le domaine est connu de la base API, mais pas de OX")

        ctx.create_user(
            givenName=mailbox.givenName,
            surName=mailbox.surName,
            username=user_name,
            domain=domain_name,
        )

    password = secrets.token_urlsafe(12)
    imap_user = sql_dovecot.create_user(db, user_name, domain_name, password)

    return web_models.NewMailbox(
        email=imap_user.username + "@" + imap_user.domain,
        password=password,
        uuid=uuid.uuid4(),
    )

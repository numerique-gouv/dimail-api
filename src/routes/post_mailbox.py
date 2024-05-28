import logging
import secrets
import uuid

import fastapi

from .. import auth, oxcli, sql_dovecot, utils, web_models
from . import DependsDovecotDb, mailboxes


@mailboxes.post("/", description="Create a mailbox in dovecot and OX", status_code=201)
async def post_mailbox(
    mailbox: web_models.CreateMailbox,
    user: auth.DependsTokenUser,
    db: DependsDovecotDb,
) -> web_models.NewMailbox:
    log = logging.getLogger(__name__)

    try:
        (username, domain) = utils.split_email(mailbox.email)
    except Exception as e:
        log.info("Failed to split the email address")
        raise fastapi.HTTPException(status_code=422, detail="Invalid email address")

    perms = user.get_creds()
    if not perms.can_read(domain):
        log.info(f"Cet utilisateur ne peut pas traiter le domaine {domain}")
        raise fastapi.HTTPException(status_code=403, detail="Permisison denied")

    ox_cluster = oxcli.OxCluster()
    ctx = ox_cluster.get_context_by_domain(domain)
    if ctx is None:
        log.error(f"Le domaine {domain} est inconnu du cluster OX")
        raise Exception("Le domaine est connu de la base API, mais pas de OX")

    ctx.create_user(
        givenName=mailbox.givenName,
        surName=mailbox.surName,
        username=username,
        domain=domain,
    )

    password = secrets.token_urlsafe(12)
    imap_user = sql_dovecot.create_dovecot_user(db, username, domain, password)

    return web_models.NewMailbox(
        email=imap_user.username + "@" + imap_user.domain,
        password=password,
        uuid=uuid.uuid4(),
    )

import logging
import uuid
import re

import fastapi

from .. import auth, oxcli, sql_dovecot, web_models
from . import DependsDovecotDb, mailboxes

mail_re = re.compile("^(?P<username>[^@]+)@(?P<domain>[^@]+)$")


@mailboxes.post(
    "/",
    description="Create a mailbox in dovecot and OX",
)
async def post_mailbox(
    mailbox: web_models.CreateMailbox,
    user: auth.DependsTokenUser,
    db: DependsDovecotDb,
) -> web_models.Mailbox:
    log = logging.getLogger(__name__)

    test_mail = mail_re.match(mailbox.email)
    if test_mail is None:
        log.info("Ca n'a pas une tete d'adresse mail.")
        raise fastapi.HTTPException(status_code=422, detail="Invalid email address")

    infos = test_mail.groupdict()
    domain = infos["domain"]
    username = infos["username"]

    perms = user.get_creds()
    if not perms.can_read(domain):
        log.info(f"Cet utilisateur ne peut pas traiter le domaine {domain}")
        raise fastapi.HTTPException(status_code=403, detail="Permisison denied")

    ox_cluster = oxcli.OxCluster()
    ctx = ox_cluster.get_context_by_domain(domain)
    if ctx is None:
        log.error(f"Le domaine {domain} est inconnu du cluster OX")
        raise Exception("Le domaine est connu de la base API, mais pas de OX")

    ox_user = ctx.create_user(
        givenName=mailbox.givenName,
        surName=mailbox.surName,
        username=username,
        domain=domain,
    )

    password = "GenerateARandomPassword"
    imap_user = sql_dovecot.create_dovecot_user(db, username, domain, password)

    return web_models.Mailbox(
        type="mailbox",
        status="ok",
        email=imap_user.username + "@" + imap_user.domain,
        givenName=ox_user.givenName,
        surName=ox_user.surName,
        domain=imap_user.domain,
        uuid=uuid.uuid4(),
    )

###     imap = sql_dovecot.get_dovecot_user(db, username, domain)
###     if imap is None:
###         log.info("La base dovecot ne contient pas cette adresse.")
###         raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")
### 
###     log.info("On a trouve l'adresse.")
###     return web_models.Mailbox(
###         type="mailbox",
###         status="ok",
###         email=imap.username + "@" + imap.domain,
###         givenName=None,
###         surName=None,
###         displayName=None,
###         username=imap.username,
###         domain=imap.domain,
###         uuid=uuid.uuid4(),
###     )
### 
### 
### #    if (
### #        mailbox_id != "toto@example.com"
### #        and mailbox_id != "d437abd5-2b49-47db-be49-05f79f1cc242"
### #    ):
### #        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")
### #
### #    return mailbox

import logging
import uuid

import fastapi

from .. import auth, oxcli, sql_dovecot, utils, web_models
from . import DependsDovecotDb, mailboxes

# uuid_re = re.compile("^[0-9a-f-]{32,36}$")


@mailboxes.get(
    "/{mailbox_id}",
    responses={
        200: {"description": "Get a mailbox from their e-mail"},
        403: {"description": "Permission denied"},
        404: {"description": "Mailbox not found"},
        422: {"description": "Email address is not well formed"},
    },
    description="The expected mailbox_id can be the e-mail address or the uuid of a mailbox",
)
async def get_mailbox(
    mailbox_id: str,
    user: auth.DependsTokenUser,
    db: DependsDovecotDb,
    # alias_db: typing.Annotated[typing.Any, fastapi.Depends(sql_alias.get_alias_db)],
) -> web_models.Mailbox:
    log = logging.getLogger(__name__)
    log.info(f"Nous cherchons qui est {mailbox_id}")
    perms = user.get_creds()
    log.info(f"Nous avons comme permissions: {perms}")
    #    test_uuid = uuid_re.match(mailbox_id)
    #    domain = None
    #    if test_uuid is not None:
    #        print("Ca ressemble a un uuid")
    #        # We try to parse the uuid (which is good enough to match the regexp)
    #        # if it is valid, and is the uuid of an existing mailbox, we go on for this mailbox
    #        id = None
    #        try:
    #            id = uuid.UUID(mailbox_id)
    #        except:
    #            print("Je n'arrive pas a parser cet uuid")
    #            pass
    #
    #        # we do not have uuid on mailboxes yet
    #        if False: # id == mailbox.uuid:
    #            print("C'est l'uuid de la seule boite que je connais")
    #            domain = mailbox.domain
    #        else:
    #            raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    try:
        (username, domain) = utils.split_email(mailbox_id)
    except Exception:
        log.info("Failed to split the email address")
        raise fastapi.HTTPException(status_code=422, detail="Invalid email address")

    log.info(f"Cette adresse est sur le domaine {domain}")

    if domain is None:
        log.error(
            "Comment ca le domaine n'est pas defini alors que ca match la regexp ?"
        )
        raise fastapi.HTTPException(status_code=422, detail="Invalid email address")

    if not perms.can_read(domain):
        log.info(f"Permission denied on domain {domain} for curent user")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    ox_cluster = oxcli.OxCluster()
    ctx = ox_cluster.get_context_by_domain(domain)
    if ctx is None:
        log.info("Aucun context ne gere le domaine chez OX")
    else:
        ox_user = ctx.get_user_by_email(mailbox_id)
        if ox_user is None:
            log.info("Le contexte ne connait pas cet email")
        else:
            log.info(f"J'ai trouve le user chez OX: {ox_user}")

    imap = sql_dovecot.get_user(db, username, domain)
    if imap is None:
        log.info("La base dovecot ne contient pas cette adresse.")
        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    log.info("On a trouve l'adresse.")
    return web_models.Mailbox(
        type="mailbox",
        status="ok",
        email=imap.username + "@" + imap.domain,
        givenName=None,
        surName=None,
        displayName=None,
        username=imap.username,
        domain=imap.domain,
        uuid=uuid.uuid4(),
    )


#    if (
#        mailbox_id != "toto@example.com"
#        and mailbox_id != "d437abd5-2b49-47db-be49-05f79f1cc242"
#    ):
#        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")
#
#    return mailbox

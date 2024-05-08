import logging
import re
import typing
import uuid

import fastapi
import sqlalchemy

from .. import sql_api
from .. import sql_dovecot
from . import get_creds, mailboxes
from .mailbox import Mailbox

mail_re = re.compile("^(?P<username>[^@]+)@(?P<domain>[^@]+)$")
uuid_re = re.compile("^[0-9a-f-]{32,36}$")


@mailboxes.get(
    "/{mailbox_id}",
    responses={
        200: {"description": "Get a mailbox from his e_mail"},
        403: {"description": "Permission denied"},
        404: {"description": "Mailbox not found"},
    },
    description="The expected mailbox_id can be the e-mail address of the uuid of a mailbox",
)
async def get_mailbox(
    mailbox_id: str,
    perms: typing.Annotated[sql_api.Creds, fastapi.Depends(get_creds)],
    db: typing.Annotated[typing.Any, fastapi.Depends(sql_dovecot.get_dovecot_db)],
) -> Mailbox:
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

    log.info(f"Nous cherchons qui est {mailbox_id}")
    #    test_uuid = uuid_re.match(mailbox_id)
    test_mail = mail_re.match(mailbox_id)
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

    if test_mail is None:
        log.info("Ca n'a pas une tete d'adresse mail.")
        raise fastapi.HTTPException(status_code=422, detail="Invalid email address")

    log.info("Ca ressemble a une adresse mail")
    infos = test_mail.groupdict()
    domain = infos["domain"]
    username = infos["username"]
    log.info(f"Cette adresse est sur le domaine {domain}")

    if domain is None:
        log.error(
            f"Comment ca le domaine n'est pas defini alors que ca match la regexp ?"
        )
        raise fastapi.HTTPException(status_code=422, detail="Invalid email address")

    if not perms.can_read(domain):
        log.info(f"Permission denied on domain {domain} for curent user")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    imap = sql_dovecot.get_dovecot_user(db, infos["username"], infos["domain"])
    if imap is None:
        log.info("La base dovecot ne contient pas cette adresse.")
        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    log.info("On a trouve l'adresse.")
    return Mailbox(
        type="mailbox",
        status="broken (only imap)",
        email=imap.username + "@" + imap.domain,
        givenName=None,
        surName=None,
        displayName=None,
        username=imap.username,
        domain=imap.domain,
        uuid=uuid.UUID4(),
    )


#    if (
#        mailbox_id != "toto@example.com"
#        and mailbox_id != "d437abd5-2b49-47db-be49-05f79f1cc242"
#    ):
#        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")
#
#    return mailbox
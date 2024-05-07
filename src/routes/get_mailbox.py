import re
import uuid
import fastapi

from .. import creds

from . import mailboxes
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
    perms: creds.Creds = fastapi.Depends(creds.get_creds),
) -> Mailbox:

    print(f"Nous cherchons qui est {mailbox_id}")
    test_uuid = uuid_re.match(mailbox_id)
    test_mail = mail_re.match(mailbox_id)
    mailbox = Mailbox(
        type="mailbox",
        email="toto@example.com",
        givenName="Given",
        surName="Sur",
        displayName="Given Sur",
        username="toto",
        domain="example.com",
        uuid=uuid.UUID("d437abd5-2b49-47db-be49-05f79f1cc242"),
    )
    domain = None
    if test_uuid is not None:
        print("Ca ressemble a un uuid")
        # We try to parse the uuid (which is good enough to match the regexp)
        # if it is valid, and is the uuid of an existing mailbox, we go on for this mailbox
        id = None
        try:
            id = uuid.UUID(mailbox_id)
        except:
            print("Je n'arrive pas a parser cet uuid")
            pass

        # we have only one mailbox here :)
        if id == mailbox.uuid:
            print("C'est l'uuid de la seule boite que je connais")
            domain = mailbox.domain
        else:
            raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    if test_mail is not None:
        print("Ca ressemble a une adresse mail")
        infos = test_mail.groupdict()
        domain = infos["domain"]
        print(f"Cette adresse est sur le domaine {domain}")

    if domain is None:
        raise fastapi.HTTPException(status_code=422, detail="Invalid email address")

    if not perms.can_read(domain):
        print(f"Permission denied on domain {domain}")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    if (
        mailbox_id != "toto@example.com"
        and mailbox_id != "d437abd5-2b49-47db-be49-05f79f1cc242"
    ):
        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    return mailbox

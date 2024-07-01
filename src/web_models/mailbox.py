import enum

import pydantic
from .. import sql_dovecot


class MailboxType(enum.StrEnum):
    Alias = "alias"
    Mailbox = "mailbox"


class MailboxStatus(enum.StrEnum):
    OK = "ok"
    Broken = "broken"


class Mailbox(pydantic.BaseModel):
    type: MailboxType
    status: MailboxStatus
    email: str
    givenName: str | None = None
    surName: str | None = None
    displayName: str | None = None
    # username: str | None = None
    # domain: str | None = None
    # uuid: pydantic.UUID4

    @classmethod
    def from_db(cls, in_db: sql_dovecot.ImapUser, username: str):
        return cls(
            type="mailbox",
            status="ok" if in_db.active == "Y" else "ko",
            email=f"{in_db.username}@{in_db.domain}",
            # givenName= in_db.givenName,
            # surName= in_db.surName,
            # displayName= in_db.displayName,
            # username= in_db.username,
            # domain= in_db.domain,
            # uuid="c324fc9b-92df-4454-8fd7-130419f80f88"
        )


class CreateMailbox(pydantic.BaseModel):
    email: str
    givenName: str
    surName: str
    displayName: str


class NewMailbox(pydantic.BaseModel):
    email: str
    password: str
    uuid: pydantic.UUID4

import enum

import pydantic


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
    username: str | None = None
    domain: str | None = None
    uuid: pydantic.UUID4

class CreateMailbox(pydantic.BaseModel):
    email: str
    givenName: str
    surName: str
    displayName: str



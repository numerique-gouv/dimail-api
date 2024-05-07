import enum
import pydantic

class MailboxType(enum.StrEnum):
    Alias = "alias"
    Mailbox = "mailbox"

class Mailbox(pydantic.BaseModel):
    type: MailboxType
    email: str
    givenName: str | None = None
    surName: str | None = None
    displayName: str | None = None
    username: str | None = None
    domain: str | None = None
    uuid: pydantic.UUID4

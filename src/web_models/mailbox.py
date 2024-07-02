import enum

import pydantic
from .. import sql_dovecot
from .. import oxcli


class MailboxType(enum.StrEnum):
    Alias = "alias"
    Mailbox = "mailbox"


class MailboxStatus(enum.StrEnum):
    OK = "ok"
    Broken = "broken"
    Unknown = "unknown"


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
            status="unknown" if in_db.active == "Y" else "ko",
            email=f"{in_db.username}@{in_db.domain}",
        )

    @classmethod
    def from_ox_user(cls, in_user: oxcli.OxUser):
        return cls(
            type="mailbox",
            status="unknown",
            email=in_user.email,
            givenName=in_user.givenName,
            surName=in_user.surName,
            displayName=in_user.displayName,
            username=in_user.username,
        )

    @classmethod
    def from_both_users(
            cls, in_ox_user: oxcli.OxUser | None,
            in_db_user: sql_dovecot.ImapUser | None):
        return cls(
            type="mailbox",
            status="ok" if in_db_user and in_ox_user else "broken",
            email=in_ox_user.email if in_ox_user else in_db_user.email(),
            givenName=in_ox_user.givenName if in_ox_user else None,
            surName=in_ox_user.surName if in_ox_user else None,
            displayName=in_ox_user.displayName if in_ox_user else None,
            username=in_db_user.username if in_db_user else None,
        )

    def __eq__(self, other):
        return isinstance(self, Mailbox) and self.email == other.email

    def __hash__(self):
        return hash(self.email)


class CreateMailbox(pydantic.BaseModel):
    email: str
    givenName: str
    surName: str
    displayName: str


class NewMailbox(pydantic.BaseModel):
    email: str
    password: str
    uuid: pydantic.UUID4

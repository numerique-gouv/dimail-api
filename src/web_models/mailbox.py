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
            type=MailboxType.Mailbox,
            status=MailboxStatus.Unknown if in_db.active == "Y" else MailboxStatus.Broken,
            email=f"{in_db.username}@{in_db.domain}",
        )

    @classmethod
    def from_ox_user(cls, in_user: oxcli.OxUser):
        return cls(
            type=MailboxType.Mailbox,
            status=MailboxStatus.Unknown,
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
        if in_ox_user is None and in_db_user is None:
            raise Exception("At least one of DB or OX user must be provided")
        email = ""
        if in_ox_user:
            email = in_ox_user.email
        else:
            email = in_db_user.email()
        self = cls(
            type=MailboxType.Mailbox,
            status=MailboxStatus.Broken,
            email=email,
        )
        if in_ox_user:
            self.givenName = in_ox_user.givenName
            self.surName = in_ox_user.surName
            self.displayName = in_ox_user.displayName
            self.username = in_db_user.username

        if in_db_user and in_ox_user:
            self.status = MailboxStatus.OK
        return self

    def __eq__(self, other):
        return isinstance(self, Mailbox) and self.email == other.email

    def __hash__(self):
        return hash(self.email)


class CreateMailbox(pydantic.BaseModel):
    givenName: str
    surName: str
    displayName: str


class NewMailbox(pydantic.BaseModel):
    email: str
    password: str
    uuid: pydantic.UUID4

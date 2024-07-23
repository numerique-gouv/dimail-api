"""This module contains the pydantic models for the mailbox.

The mailbox is a model that represents a mailbox in the system.
It can be either an alias or a mailbox.
The mailbox can be in different states, such as OK, Broken, or Unknown.

The mailbox can be created from both the OX user and the Dovecot user.
The mailbox can be created from the OX user and the Dovecot user,
and the mailbox can be created from the OX user and the Dovecot user.

The mailbox can be created from the OX user and the Dovecot user,
and the mailbox can be created from the OX user and the Dovecot user.

Classes:
    MailboxType: Enum class that represents the type of the mailbox.
    MailboxStatus: Enum class that represents the status of the mailbox.
    Mailbox: Pydantic model that represents the mailbox.
    CreateMailbox: Pydantic model that represents the creation of a mailbox.
    NewMailbox: Pydantic model that represents the new mailbox.
    UpdateMailbox: Pydantic model that represents the update of a mailbox.
"""
import enum

import pydantic
from .. import sql_dovecot
from .. import oxcli


class MailboxType(enum.StrEnum):
    """Enum class that represents the type of the mailbox.

    The mailbox can be either an alias or a mailbox.

    Attributes:
        Alias: The mailbox is an alias.
        Mailbox: The mailbox is a mailbox.
    """
    Alias = "alias"
    Mailbox = "mailbox"


class MailboxStatus(enum.StrEnum):
    """Enum class that represents the status of the mailbox.

    The mailbox can be in different states, such as OK, Broken, or Unknown.

    Attributes:
        OK: The mailbox is OK.
        Broken: The mailbox is broken.
        Unknown: The mailbox is unknown
    """
    OK = "ok"
    Broken = "broken"
    Unknown = "unknown"


class Mailbox(pydantic.BaseModel):
    """Pydantic model that represents the mailbox.

    The mailbox is a model that represents a mailbox in the system.

    Attributes:
        type: MailboxType: The type of the mailbox.
        status: MailboxStatus: The status of the mailbox.
        email: str: The email of the mailbox.
        givenName: str | None: The given name of the mailbox.
        surName: str | None: The surname of the mailbox.
        displayName: str | None: The display name of the mailbox.

    Methods:
        - from_both_users: Class method that creates a mailbox
        from both the OX user and the Dovecot user.
    """
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
    def from_both_users(
            cls,
            in_ox_user: oxcli.OxUser | None,
            in_db_user: sql_dovecot.ImapUser | None,
            webmail: bool = True,
    ):
        """Class method that creates a mailbox from both the OX user and the Dovecot user.

        Args:
            in_ox_user: oxcli.OxUser | None: The OX user.
            in_db_user: sql_dovecot.ImapUser | None: The Dovecot user.
            webmail: bool: The webmail flag.

        Returns:
            Mailbox: The mailbox.

        Raises:
            Exception: If at least one of DB or OX user must be provided.
            Exception: If the two users you provided do not have the same email address.
        """
        if in_ox_user is None and in_db_user is None:
            raise Exception("At least one of DB or OX user must be provided")
        if in_ox_user and in_db_user and not in_db_user.email() == in_ox_user.email:
            raise Exception("The two users you provided do not have the same email address")

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

        if webmail and in_db_user and in_ox_user:
            self.status = MailboxStatus.OK
        if not webmail and in_db_user and in_ox_user is None:
            self.status = MailboxStatus.OK
        return self

    def __eq__(self, other):
        return isinstance(self, Mailbox) and self.email == other.email

    def __hash__(self):
        return hash(self.email)


class CreateMailbox(pydantic.BaseModel):
    """Pydantic model that represents the creation of a mailbox.

    Attributes:
        givenName: str: The given name of the mailbox.
        surName: str: The surname of the mailbox.
        displayName: str: The display name of the mailbox.
    """
    givenName: str
    surName: str
    displayName: str


class NewMailbox(pydantic.BaseModel):
    """Pydantic model that represents the new mailbox.

    Attributes:
        email: str: The email of the mailbox.
        password: str: The password of the mailbox.
        uuid: pydantic.UUID4: The UUID of the mailbox.
    """
    email: str
    password: str
    uuid: pydantic.UUID4


class UpdateMailbox(pydantic.BaseModel):
    """Pydantic model that represents the update of a mailbox.

    Attributes:
        domain: str | None: The domain of the mailbox.
        user_name: str | None: The username of the mailbox.
        givenName: str | None: The given name of the mailbox.
        surName: str | None: The surname of the mailbox.
        displayName: str | None: The display name of the mailbox.
    """
    domain: str | None = None
    user_name: str | None = None
    givenName: str | None = None
    surName: str | None = None
    displayName: str | None = None


"""This module contains the admin models.

Classes:
    - Allowed(pydantic.BaseModel): Allowed model.
    - CreateUser(pydantic.BaseModel): CreateUser model.
    - Domain(pydantic.BaseModel): Domain model.
    - Feature(enum.StrEnum): Feature model.
    - Token(pydantic.BaseModel): Token model.
    - User(pydantic.BaseModel): User model.
"""
import enum
import uuid

import pydantic

from .. import sql_api


class Feature(enum.StrEnum):
    """Feature enumeration.

    Attributes:
        Webmail: Webmail feature.
        Mailbox: Mailbox feature.
        Alias: Alias feature.
    """
    Webmail = "webmail"
    Mailbox = "mailbox"
    Alias = "alias"


class Token(pydantic.BaseModel):
    """Token model.

    Attributes:
        access_token (str): Access token.
        token_type (str): Token type.
    """
    access_token: str
    token_type: str


class User(pydantic.BaseModel):
    """User model.

    Attributes:
        name (str): User name.
        is_admin (bool): Admin flag.
        uuid (uuid.UUID): User UUID.

    Methods:
        from_db(cls, in_db: sql_api.DBUser): Create a User model from a DBUser model.
    """
    name: str
    is_admin: bool
    uuid: uuid.UUID

    @classmethod
    def from_db(cls, in_db: sql_api.DBUser):
        """Transform a DBUser model into a User model.

        Args:
            in_db (sql_api.DBUser): DBUser model.

        Returns:
            User: User model.

        Example:

            >>> user = User.from_db(
            >>>     DBUser(name="user",
            >>>     is_admin=False,
            >>>     uuid=uuid.UUID("12345678-1234-5678-1234-567812345678")))
            >>> print(user.name)
        """
        return cls(
            name=in_db.name,
            is_admin=in_db.is_admin,
            uuid=in_db.uuid,
        )


class CreateUser(pydantic.BaseModel):
    """CreateUser model.

    Attributes:
        name (str): User name.
        password (str): User password.
        is_admin (bool): Admin flag.

    Example:
        >>> user = CreateUser(name="user", password="password", is_admin=False)
        >>> print(user.name)
    """
    name: str
    password: str
    is_admin: bool


class UpdateUser(pydantic.BaseModel):
    """UpdateUser model.

    Attributes:
        name (str): User name.
        password (str): User password.
        is_admin (bool): Admin flag.

    Example:
        >>> user = UpdateUser(name="user", password="password", is_admin=False)
        >>> print(user.name)
    """
    password: str | None = None
    is_admin: bool | None = None


class Domain(pydantic.BaseModel):
    """Domain model.

    Attributes:
        name (str): Domain name.
        features (list[Feature]): List of features.
        mailbox_domain (str): Mailbox domain.
        webmail_domain (str): Webmail domain.
        imap_domains (list[str]): IMAP domains.
        smtp_domains (list[str]): SMTP domains.
        context_name (str): Context name.

    Methods:
        from_db(Domain): Create a Domain model from a DBDomain model.

    Example:
        >>> domain = Domain(name="example.com",
        >>>               features=[Feature.Mailbox],
        >>>               mailbox_domain="example.com",
        >>>               webmail_domain="webmail.example.com",
        >>>               imap_domains=["imap.example.com"],
        >>>               smtp_domains=["smtp.example.com"],
        >>>               context_name="example")
        >>> print(domain.name)
    """
    name: str
    features: list[Feature]
    mailbox_domain: str | None = None
    webmail_domain: str | None = None
    imap_domains: list[str] | None = None
    smtp_domains: list[str] | None = None
    context_name: str | None

    @classmethod
    def from_db(cls, in_db: sql_api.DBDomain, ctx_name: str | None = None):
        """Transform a DBDomain model into a Domain model.

        Args:
            in_db (sql_api.DBDomain): DBDomain model.
            ctx_name (str | None): Context name.

        Returns:
            Domain: Domain model.

        Example:
            >>> domain = Domain.from_db(
            >>>     DBDomain(name="example.com",
            >>>     features=[Feature.Mailbox],
            >>>     mailbox_domain="example.com",
            >>>     webmail_domain="webmail.example.com",
            >>>     imap_domains=["imap.example.com"],
            >>>     smtp_domains=["smtp.example.com"]),
            >>>     ctx_name="example")
            >>> print(domain.name)
        """
        return cls(
            name=in_db.name,
            features=in_db.features,
            mailbox_domain=in_db.mailbox_domain,
            webmail_domain=in_db.webmail_domain,
            imap_domains=in_db.imap_domains,
            smtp_domains=in_db.smtp_domains,
            context_name=ctx_name,
        )


class Allowed(pydantic.BaseModel):
    """Allowed model.

    Attributes:
        user (str): User name.
        domain (str): Domain name.

    Methods:
        from_db(Allowed): Create an Allowed model from a DBAllowed model.

    Example:
        >>> allowed = Allowed(user="user", domain="example.com")
        >>> print(allowed.user)
    """
    user: str
    domain: str

    @classmethod
    def from_db(cls, in_db: sql_api.DBAllowed):
        """Transform a DBAllowed model into an Allowed model.

        Args:
            in_db (sql_api.DBAllowed): DBAllowed model.

        Returns:
            Allowed: Allowed model.

        Example:
            >>> allowed = Allowed.from_db(
            >>>     DBAllowed(user="user", domain="example.com"))
            >>> print(allowed.user)
        """
        return cls(
            user=in_db.user,
            domain=in_db.domain,
        )

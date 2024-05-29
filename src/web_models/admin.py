import enum
import uuid

import pydantic

from .. import sql_api


class Feature(enum.StrEnum):
    Webmail = "webmail"
    Mailbox = "mailbox"
    Alias = "alias"


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class User(pydantic.BaseModel):
    name: str
    is_admin: bool
    uuid: uuid.UUID

    @classmethod
    def from_db(cls, in_db: sql_api.DBUser):
        return cls(
            name=in_db.name,
            is_admin=in_db.is_admin,
            uuid=in_db.uuid,
        )


class CreateUser(pydantic.BaseModel):
    name: str
    password: str
    is_admin: bool


class Domain(pydantic.BaseModel):
    name: str
    features: list[Feature]
    mailbox_domain: str | None = None
    webmail_domain: str | None = None
    imap_domains: list[str] | None = None
    smtp_domains: list[str] | None = None
    context_name: str | None

    @classmethod
    def from_db(cls, in_db: sql_api.DBDomain, ctx_name: str | None = None):
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
    user: str
    domain: str

    @classmethod
    def from_db(cls, in_db: sql_api.DBAllowed):
        return cls(
            user=in_db.user,
            domain=in_db.domain,
        )


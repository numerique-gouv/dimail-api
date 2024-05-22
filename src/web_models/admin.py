import enum
import uuid

import pydantic


class Feature(enum.StrEnum):
    Webmail = "webmail"
    Mailbox = "mailbox"
    Alias = "alias"


class WToken(pydantic.BaseModel):
    access_token: str
    token_type: str

    class ConfigDict:
        from_attribute = True


class WUser(pydantic.BaseModel):
    name: str
    is_admin: bool
    uuid: uuid.UUID

    class ConfigDict:
        from_attribute = True


class CreateUser(pydantic.BaseModel):
    name: str
    password: str
    is_admin: bool


class WDomain(pydantic.BaseModel):
    name: str
    features: list[Feature]
    mailbox_domain: str | None = None
    webmail_domain: str | None = None
    imap_domains: list[str] | None = None
    smtp_domains: list[str] | None = None
    context_name: str | None

    class ConfigDict:
        from_attribute = True


class WAllowed(pydantic.BaseModel):
    user: str
    domain: str

    class ConfigDict:
        from_attribute = True

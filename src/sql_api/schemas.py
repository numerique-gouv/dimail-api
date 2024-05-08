import enum
import pydantic


class Feature(enum.StrEnum):
    Webmail = "webmail"
    Mailbox = "mailbox"
    Alias = "alias"


class ApiUser(pydantic.BaseModel):
    name: str
    is_admin: bool

    class ConfigDict:
        from_attribute = True


class ApiDomain(pydantic.BaseModel):
    name: str
    features: list[Feature]
    mailbox_domain: str | None = None
    webmail_domain: str | None = None
    imap_domains: list[str] | None = None
    smtp_domains: list[str] | None = None

    class ConfigDict:
        from_attribute = True


class ApiAllowed(pydantic.BaseModel):
    user: str
    domain: str

    class ConfigDict:
        from_attribute = True

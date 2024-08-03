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


class UpdateUser(pydantic.BaseModel):
    password: str | None = None
    is_admin: bool | None = None


class TestErr(pydantic.BaseModel):
    code: str
    detail: str

class TestResult(pydantic.BaseModel):
    ok: bool = True
    errors: list[TestErr] = []

    def add_err(self, err):
        self.ok = False
        self.errors.append(TestErr(code=err["code"], detail=err["detail"]))

class CreateDomain(pydantic.BaseModel):
    name: str
    features: list[Feature]
    mailbox_domain: str | None = None
    webmail_domain: str | None = None
    imap_domains: list[str] | None = None
    smtp_domains: list[str] | None = None
    context_name: str | None

all_tests = [ "domain_exist", "mx", "cname_imap", "cname_smtp", "cname_webmail", "spf", "dkim" ]
class Domain(pydantic.BaseModel):
    name: str
    state: str
    valid: bool = True

    features: list[Feature]
    mailbox_domain: str | None = None
    webmail_domain: str | None = None
    imap_domains: list[str] | None = None
    smtp_domains: list[str] | None = None
    context_name: str | None

    domain_exist: TestResult = TestResult()
    mx: TestResult = TestResult()
    cname_imap: TestResult = TestResult()
    cname_smtp: TestResult = TestResult()
    cname_webmail: TestResult = TestResult()
    spf: TestResult = TestResult()
    dkim: TestResult = TestResult()

    def add_errors(self, errors: list):
        if errors is None:
            return
        for err in errors:
            self.valid = False
            getattr(self, err["test"]).add_err(err)

    @classmethod
    def from_db(cls, in_db: sql_api.DBDomain, ctx_name: str | None = None):
        self = cls(
            name=in_db.name,
            state=in_db.state,
            features=in_db.features,
            mailbox_domain=in_db.mailbox_domain,
            webmail_domain=in_db.webmail_domain,
            imap_domains=in_db.imap_domains,
            smtp_domains=in_db.smtp_domains,
            context_name=ctx_name,
        )
        if in_db.state == "new":
            self.valid = False
        if in_db.dtchecked is None:
            for test in all_tests:
                getattr(self, test).add_err({"code": "no_test", "detail": "Did not check yet"})
        if in_db.errors is not None:
            self.add_errors(in_db.errors)
        return self


class Allowed(pydantic.BaseModel):
    user: str
    domain: str

    @classmethod
    def from_db(cls, in_db: sql_api.DBAllowed):
        return cls(
            user=in_db.user,
            domain=in_db.domain,
        )

import datetime
import uuid

import jwt
import passlib.hash

# from passlib.hash import argon2
import sqlalchemy as sa
import sqlalchemy.orm as orm

from .. import config
from .creds import Creds
from .database import Api


class DBUser(Api):
    __tablename__ = "users"
    __table_args__ = (sa.UniqueConstraint("uuid", name="uuid_is_unique"),)
    name = sa.Column(sa.String(32), primary_key=True)
    uuid = sa.Column(sa.UUID, default=uuid.uuid4)
    hashed_password = sa.Column(sa.String(128), nullable=True)
    is_admin = sa.Column(sa.Boolean, default=False)
    fullname = sa.Column(sa.String(64), nullable=True)
    domains: orm.Mapped[list["DBDomain"]] = orm.relationship(
        secondary="allowed", back_populates="users"
    )

    def __eq__(self, other):
        if not isinstance(self, other.__class__):
            return False
        if (
            self.name == other.name
            and self.is_admin == other.is_admin
            and self.fullname == other.fullname
        ):
            return True
        return False

    def set_password(self, password: str):
        self.hashed_password = passlib.hash.argon2.hash(password)

    def verify_password(self, password: str):
        return passlib.hash.argon2.verify(password, self.hashed_password)

    def create_token(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = datetime.timedelta(minutes=47)
        expire = now + delta
        data = {
            "sub": self.name,
            "exp": expire,
        }
        secret = config.settings["JWT_SECRET"]
        algo = "HS256"
        return jwt.encode(data, secret, algo)

    def get_creds(self) -> Creds:
        if self.is_admin:
            # log.info(f"The user {user_name} is an admin")
            return Creds(is_admin=True)
        domains = self.domains
        creds = Creds(domains=[])
        creds.domains = [dom.name for dom in domains]
        # log.info(f"Non-admin user {user_name}, {creds}")
        return creds


class DBDomain(Api):
    __tablename__ = "domains"
    name = sa.Column(sa.String(200), primary_key=True)
    features = sa.Column(sa.JSON(), nullable=False)
    webmail_domain = sa.Column(sa.String(200), nullable=True)
    mailbox_domain = sa.Column(sa.String(200), nullable=True)
    imap_domains = sa.Column(sa.JSON(), nullable=True)
    smtp_domains = sa.Column(sa.JSON(), nullable=True)
    state = sa.Column(sa.String(15), nullable=False, default="new")
    errors = sa.Column(sa.JSON(), nullable=True)
    dtcreated = sa.Column(sa.DateTime(), nullable=False, server_default=sa.sql.func.now())
    dtupdated = sa.Column(sa.DateTime(), nullable=False, server_default=sa.sql.func.now(), onupdate=sa.sql.func.now())
    dtchecked = sa.Column(sa.DateTime(), nullable=True)
    dtaction = sa.Column(sa.DateTime(), nullable=True, index=True)
    users: orm.Mapped[list["DBUser"]] = orm.relationship(
        secondary="allowed", back_populates="domains"
    )

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def get_webmail_domain(self) -> str:
        if self.webmail_domain is not None:
            return self.webmail_domain
        return "webmail." + self.name

    def get_mailbox_domain(self) -> str:
        if self.mailbox_domain is not None:
            return self.mailbox_domain
        return self.name

    def get_alias_domain(self) -> str:
        return self.name

    def get_imap_domains(self) -> list[str]:
        if self.imap_domain is not None:
            return self.imap_domains
        return [ "imap." + self.name ]

    def get_smtp_domains(self) -> list[str]:
        if self.smtp_domains is not None:
            return self.smtp_domains
        return [ "smtp." + self.name ]

    def get_domain(self, what: str) -> str | list[str]:
        if what == "mailbox":
            return self.get_mailbox_domain()
        if what == "alias":
            return self.get_alias_domain()
        if what == "imap":
            return self.get_imap_domains()
        if what == "smtp":
            return self.get_smtp_domains()
        if what == "webmail":
            return self.get_webmail_domain()

class DBAllowed(Api):
    __tablename__ = "allowed"
    user = sa.Column(sa.String(32), sa.ForeignKey("users.name"), primary_key=True)
    domain = sa.Column(
        sa.String(200),
        sa.ForeignKey("domains.name"),
        primary_key=True,
    )

    def __repr__(self):
        return 'sql_api.DBAllowed("%s","%s")' % (self.user, self.domain)

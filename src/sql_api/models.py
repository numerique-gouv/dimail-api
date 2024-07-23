"""This modules contains the models for the SQL database.

Classes:
    - DBUser: a user of the system
    - DBDomain: a domain of the system
    - DBAllowed: a many-to-many relationship between users and domains
"""
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
    """A user of the system.

    This classes modelize a users table in the database.
    Its attributes represent the different columns of the table it models

    Attributes:
        name: the username
        uuid: a unique identifier
        hashed_password: the password, hashed
        is_admin: whether the user is an admin
        fullname: the full name of the user
        domains: the domains the user has access to

    Functions:
        set_password: set the password of the user
        verify_password: verify a password against the user's password
        create_token: create a JWT token for the user
        get_creds: get the credentials
    """
    __tablename__ = "users"
    __table_args__ = (sa.UniqueConstraint("uuid", name="uuid_is_unique"),)
    name = sa.Column(sa.String(32), primary_key=True)
    uuid = sa.Column(sa.UUID, default=uuid.uuid4)
    hashed_password = sa.Column(sa.String(128, collation="ascii_bin"), nullable=True)
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

    def set_password(self, password: str) -> None:
        """Set the password of the user.

        Args:
            password: the password to set

        Returns:
            None
        """
        self.hashed_password = passlib.hash.argon2.hash(password)

    def verify_password(self, password: str)-> bool:
        """Verify a password against the user's password.

        Args:
            password: the password to verify

        Returns:
            bool: whether the password is correct
        """
        return passlib.hash.argon2.verify(password, self.hashed_password)

    def create_token(self)-> str:
        """Create a JWT token for the user.

        Returns:
            str: the JWT token
        """
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
        """Get the credentials.

        Returns:
            Creds: the credentials
        """
        if self.is_admin:
            # log.info(f"The user {user_name} is an admin")
            return Creds(is_admin=True)
        domains = self.domains
        creds = Creds(domains=[])
        creds.domains = [dom.name for dom in domains]
        # log.info(f"Non-admin user {user_name}, {creds}")
        return creds


class DBDomain(Api):
    """A domain of the system.

    This classes modelize a domains table in the database.

    Attributes:
        name: the domain name
        features: the features of the domain
        webmail_domain: the webmail domain
        mailbox_domain: the mailbox domain
        imap_domains: the IMAP domains
        smtp_domains: the SMTP domains
        users: the users that have access to the domain

    Functions:
        has_feature: check if the domain has a feature
    """
    __tablename__ = "domains"
    name = sa.Column(sa.String(200, collation="ascii_bin"), primary_key=True)
    features = sa.Column(sa.JSON(), nullable=False)
    webmail_domain = sa.Column(sa.String(200, collation="ascii_bin"), nullable=True)
    mailbox_domain = sa.Column(sa.String(200, collation="ascii_bin"), nullable=True)
    imap_domains = sa.Column(sa.JSON(), nullable=True)
    smtp_domains = sa.Column(sa.JSON(), nullable=True)
    users: orm.Mapped[list["DBUser"]] = orm.relationship(
        secondary="allowed", back_populates="domains"
    )

    def has_feature(self, feature: str) -> bool:
        """Check if the domain has a feature.

        Args:
            feature: the feature to check

        Returns:
            bool: whether the domain has the feature
        """
        return feature in self.features


class DBAllowed(Api):
    """A many-to-many relationship between users and domains.

    This classes modelize an allowed table in the database.

    Attributes:
        user: the user
        domain: the domain
    """
    __tablename__ = "allowed"
    user = sa.Column(sa.String(32), sa.ForeignKey("users.name"), primary_key=True)
    domain = sa.Column(
        sa.String(200, collation="ascii_bin"),
        sa.ForeignKey("domains.name"),
        primary_key=True,
    )

    def __repr__(self):
        return 'sql_api.DBAllowed("%s","%s")' % (self.user, self.domain)

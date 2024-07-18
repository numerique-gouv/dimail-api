"""SQLAlchemy models for Dovecot.

Classes:
    - ImapUser: a user of the system
"""
import passlib.hash
import sqlalchemy as sa
import sqlalchemy.dialects.mysql

from . import database


class ImapUser(database.Dovecot):
    """A user of the dovecot system.

    This class models a users table in the database.

    Attributes:
        username: the username
        domain: the domain of the user
        password: the password, hashed
        home: the home directory of the user
        uid: the user id
        gid: the group id
        active: whether the user is active

    Functions:
        set_password: set the password of the user
        check_password: check a password against the user's password
        email: get the email of the user
    """
    __tablename__ = "users"
    username = sa.Column(
        sa.String(128, collation="ascii_bin"), nullable=False, primary_key=True
    )
    domain = sa.Column(
        sa.String(128, collation="ascii_bin"), nullable=False, primary_key=True
    )
    password = sa.Column(sa.String(150, collation="ascii_bin"), nullable=False)
    home = sa.Column(sa.String(255, collation="ascii_bin"), nullable=False)
    uid = sa.Column(sa.Integer, nullable=False)
    gid = sa.Column(sa.Integer, nullable=False)
    active = sa.Column(
        sa.dialects.mysql.CHAR(length=1), nullable=False, server_default="Y"
    )

    def set_password(self, password: str) -> None:
        """Set the password of the user.

        Hashes the password using argon2id and sets it as the user's password.

        Args:
            password: the password to set
        """
        self.password = "{ARGON2ID}" + passlib.hash.argon2.hash(password)

    def check_password(self, password: str) -> bool:
        """Check a password against the user's password.

        Args:
            password: the password to check

        Returns:
            bool: whether the password is correct

        Raises:
            Exception: if the password was not encoded by this class
        """
        if not self.password.startswith("{ARGON2ID}"):
            raise Exception("This password was not encoded by me, i can't check it")
        return passlib.hash.argon2.verify(password, self.password[len("{ARGON2ID}") :])

    def email(self) -> str:
        """Get the email of the user.

        Returns:
            str: the email of the user

        Example:
            >>> user = ImapUser(username="test", domain="example.com")
            >>> user.email()

        """
        return self.username + "@" + self.domain

# CREATE TABLE `users` (
#   `username` varchar(128) NOT NULL,
#   `domain` varchar(128) NOT NULL,
#   `password` varchar(150) NOT NULL,
#   `home` varchar(255) NOT NULL,
#   `uid` int(11) NOT NULL,
#   `gid` int(11) NOT NULL,
#   `active` char(1) NOT NULL DEFAULT 'Y',
#   PRIMARY KEY (`username`,`domain`)
#

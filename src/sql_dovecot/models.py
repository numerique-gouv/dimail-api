import sqlalchemy as sa
import sqlalchemy.dialects.mysql
import passlib.hash

from . import database


class ImapUser(database.Dovecot):
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
        self.password = "{ARGON2ID}" + passlib.hash.argon2.hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password.startswith("{ARGON2ID}"):
            raise Exception("This password was not encoded by me, i can't check it")
        return passlib.hash.argon2.verify(password, self.password[len("{ARGON2ID}"):])


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

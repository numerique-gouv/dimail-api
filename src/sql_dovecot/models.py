import sqlalchemy as sa
import sqlalchemy.dialects.mysql

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

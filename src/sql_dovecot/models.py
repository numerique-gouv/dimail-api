from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import relationship

from .database import Dovecot


class ImapUser(Dovecot):
    __tablename__ = "users"
    username = Column(
        String(128, collation="ascii_bin"), nullable=False, primary_key=True
    )
    domain = Column(
        String(128, collation="ascii_bin"), nullable=False, primary_key=True
    )
    password = Column(String(150, collation="ascii_bin"), nullable=False)
    home = Column(String(255, collation="ascii_bin"), nullable=False)
    uid = Column(Integer, nullable=False)
    gid = Column(Integer, nullable=False)
    active = Column(mysql.CHAR(length=1), nullable=False, server_default="Y")


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

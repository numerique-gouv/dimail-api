import sqlalchemy as sa

from . import database


class Alias(database.Postfix):
    __tablename__ = "aliases"
    alias = sa.Column(sa.String(256), nullable=False, primary_key=True)
    domain = sa.Column(sa.String(128), nullable=False, index=True)
    destination = sa.Column(sa.String(256), nullable=False, primary_key=True)

class Sender(database.Postfix):
    __tablename__ = "sender_login_map"
    sender = sa.Column(sa.String(256), nullable=False, primary_key=True)
    login = sa.Column(sa.String(256), nullable=False, primary_key=True, index=True)
    domain = sa.Column(sa.String(128), nullable=False, index=True)

class MailboxDomain(database.Postfix):
    __tablename__ = "mailbox_domains"
    domain = sa.Column(sa.String(128), nullable=False, primary_key=True)
    mailbox_domain = sa.Column(sa.String(128), nullable=False, index=True)

class AliasDomain(database.Postfix):
    __tablename__ = "alias_domains"
    domain = sa.Column(sa.String(128), nullable=False, primary_key=True)
    alias_domain = sa.Column(sa.String(128), nullable=False, index=True)


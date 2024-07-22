import sqlalchemy as sa

from . import database


class PostfixAlias(database.Postfix):
    __tablename__ = "aliases"
    alias = sa.Column(sa.String(500), nullable=False, primary_key=True)
    domain = sa.Column(sa.String(100), nullable=False, index=True)
    destination = sa.Column(sa.String(500), nullable=False, primary_key=True)

"""Postfix models for SQLAlchemy ORM.

This module contains the SQLAlchemy ORM models for the Postfix database.

Classes:
    PostfixAlias: Postfix aliases table model.
"""
import sqlalchemy as sa

from . import database


class PostfixAlias(database.Postfix):
    """Postfix aliases table model.

    This class represents the aliases table in the Postfix database.

    Attributes:
        alias: The alias for the email address.
        domain: The domain for the email address.
        destination: The destination email address.
    """
    __tablename__ = "aliases"
    alias = sa.Column(sa.String(500, collation="ascii_bin"), nullable=False, primary_key=True)
    domain = sa.Column(sa.String(100, collation="ascii_bin"), nullable=False, index=True)
    destination = sa.Column(sa.String(500, collation="ascii_bin"), nullable=False, primary_key=True)

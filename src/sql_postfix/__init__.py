"""SQL Postfix package.

This package provides a SQLAlchemy ORM model for Postfix aliases.

Attributes:
    __all__ (list): List of package modules to import when using `from sql_postfix import *`.

Classes:
    PostfixAlias (SQLAlchemy model): Postfix alias model.

Functions:
    create_alias (function): Create a new alias.
    delete_alias (function): Delete an alias.
    delete_aliases_by_name (function): Delete aliases by name.
    get_alias (function): Get an alias by ID.
    get_aliases_by_domain (function): Get aliases by domain.
    get_aliases_by_name (function): Get aliases by name.
    get_maker (function): Get a SQLAlchemy session maker.
    init_db (function): Initialize the database.

Modules:
    crud (module): CRUD functions for the Postfix alias model.
    database (module): Database initialization and session maker.
    models (module): SQLAlchemy model definitions.
"""
from .crud import (
    create_alias,
    delete_alias,
    delete_aliases_by_name,
    get_alias,
    get_aliases_by_domain,
    get_aliases_by_name
)
from .database import get_maker, init_db
from .models import PostfixAlias

__all__ = [
    create_alias,
    delete_alias,
    delete_aliases_by_name,
    get_alias,
    get_aliases_by_domain,
    get_aliases_by_name,
    get_maker,
    init_db,
    PostfixAlias,
]

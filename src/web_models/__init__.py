"""Web models package.

This package contains all the web models used by the FastAPI application.

Attributes:
    __all__: List of modules to import when using `from web_models import *`

Modules:
    - admin: Admin models.
    - alias: Alias models.
    - mailbox: Mailbox models.

Classes:
    - Allowed: Allowed model.
    - CreateUser: CreateUser model.
    - Domain: Domain model.
    - Feature: Feature model.
    - Token: Token model.
    - User: User model.
    - Alias: Alias model.
    - CreateAlias: CreateAlias model.
    - CreateMailbox: CreateMailbox model.
    - Mailbox: Mailbox model.
    - MailboxStatus: MailboxStatus model.
    - MailboxType: MailboxType model.
    - NewMailbox: NewMailbox model.
    - UpdateMailbox: UpdateMailbox model.
    - UpdateUser: UpdateUser model.
"""
from .admin import Allowed, CreateUser, UpdateUser, Domain, Feature, Token, User
from .alias import Alias, CreateAlias
from .mailbox import (
    CreateMailbox,
    Mailbox,
    MailboxStatus,
    MailboxType,
    NewMailbox,
    UpdateMailbox,
)

__all__ = [
    Allowed,
    CreateAlias,
    CreateUser,
    Domain,
    Feature,
    Token,
    User,
    Alias,
    CreateMailbox,
    Mailbox,
    MailboxStatus,
    MailboxType,
    NewMailbox,
    UpdateMailbox,
    UpdateUser,
]

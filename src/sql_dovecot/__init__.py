"""SQL Alchemy models and CRUD functions for Dovecot IMAP users.

Classes:
    - ImapUser: a user of the system

Functions:
    - create_user: create a user
    - delete_user: delete a user
    - get_users: get all users
    - get_user: get a user by name
    - get_maker: get a session maker
    - init_db: initialize the database

Modules:
    - crud: functions to interact with the database
    - database: database setup
    - models: the database models
"""
from .crud import create_user, delete_user, get_user, get_users
from .database import get_maker, init_db
from .models import ImapUser

__all__ = [
    create_user,
    delete_user,
    get_users,
    get_user,
    get_maker,
    init_db,
    ImapUser,
]

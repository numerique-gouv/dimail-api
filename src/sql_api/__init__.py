"""SQL API package.

This package contains all the functions and classes to interact with the SQL
database. It is used by the API to perform all the necessary operations to
manage users, domains, and permissions.

The package is divided into modules, each one containing functions and classes
to interact with a specific part of the database. The modules are:
- `allow`: Functions to manage the permissions of users.
- `creds`: Class to handle the credentials of the database.
- `database`: Functions to initialize the database.
- `domain`: Functions to manage the domains.
- `models`: Classes to represent the database tables.
- `user`: Functions to manage the users.

The package also contains the `__all__` variable, which is a list of all the
functions and classes that are exposed by the package. This variable is used by
the `from sql_api import *` statement to import all the functions and classes
from the package.

Modules:
    allow: Functions to manage the permissions of users.
    creds: Class to handle the credentials of the database.
    database: Functions to initialize the database.
    domain: Functions to manage the domains.
    models: Classes to represent the database tables.
    user: Functions to manage the users.

Variables:
    __all__: List of all the functions and classes exposed by the package.

The Classes and Functions are:
    - allow_domain_for_user: Allow a user to access a domain.
    - delete_allows_by_user: Delete all the permissions of a user.
    - deny_domain_for_user: Deny a user to access a domain.
    - get_allowed: Get the domains that a user is allowed to access.
    - get_allows: Get all the permissions of a user.
    - Creds: Class to handle the credentials of the database.
    - get_maker: Get a database session maker.
    - init_db: Initialize the database.
    - create_domain: Create a new domain.
    - get_domain: Get a domain by its name.
    - get_domains: Get all the domains.
    - DBAllowed: Class to represent the allowed table.
    - DBDomain: Class to represent the domain table.
    - DBUser: Class to represent the user table.
    - count_users: Count the number of users.
    - create_user: Create a new user.
    - delete_user: Delete a user.
    - get_user: Get a user by its username.
    - get_users: Get all the users.
    - update_user_password: Update the password of a user.
    - update_user_is_admin: Update the admin status of a user.
"""
from .allow import (
    allow_domain_for_user,
    delete_allows_by_user,
    deny_domain_for_user,
    get_allowed,
    get_allows,
)
from .creds import Creds
from .database import get_maker, init_db
from .domain import create_domain, get_domain, get_domains
from .models import DBAllowed, DBDomain, DBUser
from .user import (
    count_users,
    create_user,
    delete_user,
    get_user,
    get_users,
    update_user_password,
    update_user_is_admin,
)

__all__ = [
    allow_domain_for_user,
    delete_allows_by_user,
    deny_domain_for_user,
    get_allowed,
    get_allows,
    Creds,
    get_maker,
    init_db,
    create_domain,
    get_domain,
    get_domains,
    DBAllowed,
    DBDomain,
    DBUser,
    count_users,
    create_user,
    delete_user,
    get_user,
    get_users,
    update_user_password,
    update_user_is_admin,
]

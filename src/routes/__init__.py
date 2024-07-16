# ruff: noqa: E402
"""Routes module for the API.

This module contains all the routes for the API. Each route is a separate
module that is imported here. This is done to keep the code clean and
organized. Each route is responsible for a specific part of the API.

The routes are imported here and then exported to the main application

Attributes:
    __all__ (list): List of all the routes that are exported to the main
    __useless__ (list): List of all the routes that are imported but not used linter.
"""
from . import aliases, allows, domains, mailboxes, users

from .get_token import login_for_access_token

# Stupid useless variable to shut up the linter
__useless__ = [
    aliases.get_alias,
    allows.get_allows,
    domains.get_domain,
    mailboxes.get_mailboxes,
    users.get_user,
]

__all__ = [
    login_for_access_token,
]

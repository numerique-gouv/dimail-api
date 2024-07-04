# ruff: noqa: E402
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

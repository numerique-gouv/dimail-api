# ruff: noqa: E402
"""This module contains the domains routes.

The domains routes are used to manage domains.

Permitted roles:
    * admin

The domains routes are:
    * GET /domains/{domain_name}
    * GET /domains
    * POST /domains
"""
from .get_domain import get_domain
from .get_domains import get_domains
from .post_domain import post_domain

__all__ = [
    get_domain,
    get_domains,
    post_domain,
]


"""This module contains the functions to manage the credentials in the database.

The credentials are the permissions given to a user to manage the mailboxes and the aliases
The credentials are stored in the table `creds` in the database. The table has the following
columns:
    - `domains`: the domains that the user is allowed to manage
    - `is_admin`: if the user is an admin

The credentials are managed the following class:
    - Creds: the credentials for a user
"""
import pydantic


class Creds(pydantic.BaseModel):
    """The credentials for a user.

    The credentials are the permissions given to a user to manage the mailboxes and the aliases

    Attributes:
        domains (list[str]): the domains that the user is allowed to manage
        is_admin (bool): if the user is an admin

    Methods:
        can_read: check if the user can read the domain
    """
    domains: list[str] = []
    is_admin: bool = False

    def can_read(self, domain: str) -> bool:
        """Check if the user can read the domain.

        If the user is an admin, the user can always read the domain.
        If the user is not an admin, the user can read the domain if the domain is in the
        domains list.

        Args:
            domain (str): the domain to check if the user can read

        Returns:
            bool: if the user can read the domain
        """
        if self.is_admin:
            return True
        if domain in self.domains:
            return True
        return False

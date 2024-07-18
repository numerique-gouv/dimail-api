"""This module contains the Alias class, which is a pydantic model for the Alias object.

Classes:
    - Alias(pydantic.BaseModel): Alias model.
    - CreateAlias(pydantic.BaseModel): CreateAlias model.
"""
import pydantic

from .. import sql_postfix, utils


class Alias(pydantic.BaseModel):
    """Alias model.

    Attributes:
        username (str): Username.
        domain (str): Domain.
        destination (str): Destination.

    Methods:
        from_db(Alias): Create an Alias model from a PostfixAlias model.
    """
    username: str
    domain: str
    destination: str

    @classmethod
    def from_db(cls, dbAlias: sql_postfix.PostfixAlias):
        """Create an Alias model from a PostfixAlias model.

        Args:
            dbAlias (PostfixAlias): PostfixAlias model.

        Returns:
            Alias: Alias model.

        Raises:
            Exception: If the alias in the database is not consistent.

        Example:
            >>> from src import sql_postfix
            >>>
            >>> Alias.from_db(
            >>>       sql_postfix.PostfixAlias(
            >>>         alias="user@domain",
            >>>         destination="user@domain",
            >>>         domain="domain"))
            >>> Alias(username="user", domain="domain", destination="user@domain")
        """
        (username, domain) = utils.split_email(dbAlias.alias)
        if domain != dbAlias.domain:
            raise Exception(
                "The alias in database is not consistend (alias and domain disagree)"
            )

        return cls(
            destination=dbAlias.destination,
            domain=dbAlias.domain,
            username=username,
        )

class CreateAlias(pydantic.BaseModel):
    """CreateAlias model.

    Attributes:
        user_name (str): User name.
        destination (str): Destination.

    Example:
        >>> create_alias = CreateAlias(user_name="user", destination="user@domain")
        >>> print(create_alias.user_name, create_alias.destination)
    """
    user_name: str
    destination: str

import pydantic

from .. import sql_postfix, utils


class Alias(pydantic.BaseModel):
    username: str
    domain: str
    destination: str

    @classmethod
    def from_db(cls, dbAlias: sql_postfix.Alias):
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
    user_name: str
    destination: str

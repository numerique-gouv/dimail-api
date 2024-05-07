import pydantic

from .. import sql_api


class Creds(pydantic.BaseModel):
    domains: list[str] = []
    is_admin: bool = False

    def can_read(self, domain: str) -> bool:
        if self.is_admin:
            return True
        if domain in self.domains:
            return True
        return False


user_name = "toto2"


async def get_creds():
    print(f"Getting creds for user {user_name}")
    db = next(sql_api.get_api_db())
    user = sql_api.get_api_user(db, user_name)
    if user is None:
        print(f"User not found")
        return Creds()
    if user.is_admin:
        print(f"The user {user_name} is an admin")
        return Creds(is_admin=True)
    domains = user.domains
    creds = Creds(domains=[])
    creds.domains = [dom.name for dom in domains]
    print(f"Non-admin user {user_name}, {creds}")
    return creds

import pydantic

from .crud import get_api_user


class Creds(pydantic.BaseModel):
    domains: list[str] = []
    is_admin: bool = False

    def can_read(self, domain: str) -> bool:
        if self.is_admin:
            return True
        if domain in self.domains:
            return True
        return False


Xuser_name = "toto2"


def set_current_user_name(name: str):
    global Xuser_name
    Xuser_name = name


def get_creds(db, log, user_name: str) -> Creds:
    log.info(f"Getting creds for user {user_name} into db {db}")
    user = get_api_user(db, user_name)
    if user is None:
        log.info(f"User {user_name} not found")
        return Creds()
    if user.is_admin:
        log.info(f"The user {user_name} is an admin")
        return Creds(is_admin=True)
    domains = user.domains
    creds = Creds(domains=[])
    creds.domains = [dom.name for dom in domains]
    log.info(f"Non-admin user {user_name}, {creds}")
    return creds

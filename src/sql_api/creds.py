import pydantic


class Creds(pydantic.BaseModel):
    domains: list[str] = []
    is_admin: bool = False

    def can_read(self, domain: str) -> bool:
        if self.is_admin:
            return True
        if domain in self.domains:
            return True
        return False



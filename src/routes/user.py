from pydantic import BaseModel, UUID4

class User(BaseModel):
  email: str
  givenName: str | None = None
  surName: str | None = None
  displayName: str | None = None
  username: str | None = None
  domain: str | None = None
  uuid: UUID4



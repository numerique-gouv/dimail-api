from pydantic import BaseModel


class Domain(BaseModel):
    name: str


class User(BaseModel):
    name: str
    email: str

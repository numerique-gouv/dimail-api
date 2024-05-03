from fastapi import APIRouter

from src.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


fake_db_users = [
    {"name": "Prudence", "email": "prudence.crandall@edu.us.com"},
    {"email": "marie@mail.fr", "name": "Marie"},
    {"email": "benjamin@mail.fr", "name": "Benjamin"},
    {"email": "sabrina@mail.fr", "name": "Sabrina"},
    {"email": "artemisia.gentilesci@arte.it", "name": "Artemisia"},
    {"email": "alexandria.ocasio-cortez@gov.us", "name": "AOC"},
]


@router.get("/", response_model=list[User])
async def get_users(offset: int = 0, limit: int = 4):
    return fake_db_users


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, user: User):
    return {"user_id": str(user_id), "user_email": "marie@mail.fr"}


@router.post("/", response_model=User)
async def create_user(data: dict) -> User:
    pass

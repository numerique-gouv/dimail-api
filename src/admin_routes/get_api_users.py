from fastapi import Depends

from sql_api import crud, database, schemas

from . import ox


@ox.get("/api/users")
async def get_api_users(
    db=Depends(database.get_api_db),
) -> list[schemas.ApiUser]:
    users = crud.get_api_users(db)
    return users

import fastapi, logging, jwt
from .. import config, sql_api, web_models

from . import usertoken


@usertoken.get("/{user_name}")
async def get_usertoken(
    user_name: str,
    db=fastapi.Depends(sql_api.get_api_db),
) -> web_models.WUserToken:
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.info(f"Nous vérifions que {user_name} existe")

    user_db = sql_api.get_api_user(db, user_name)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")

    jwt_secret = config.settings['JWT_SECRET']
    user_token = web_models.WUserToken(
        name = user_name,
        token = jwt.encode({"user_name": user_db.name}, jwt_secret),
    )

    return user_token





import datetime
import logging

import fastapi
import fastapi.security
import jwt

from .. import config, sql_api, sql_dovecot

mailboxes = fastapi.APIRouter(prefix="/mailboxes", tags=["mailboxes"])
token = fastapi.APIRouter(prefix="/token", tags=["token"])


def depends_api_db():
    """Dependency for fastapi that creates an orm session and yields it. Ensures
    the session is closed at the end."""
    maker = sql_api.get_maker()
    db = maker()
    # En cas d'erreur, on va lever une exception (404, 403, etc), or il faudra
    # quand meme fermer la connexion a la base de données
    try:
        yield db
    finally:
        db.close()


def depends_dovecot_db():
    """Dependency for fastapi that creates an orm session and yields it. Ensures
    the session is closed at the end."""
    maker = sql_dovecot.get_maker()
    db = maker()
    # En cas d'erreur, on va lever une exception (404, 403, etc), or il faudra
    # quand meme fermer la connexion a la base de données
    try:
        yield db
    finally:
        db.close()


class depends_jwt(fastapi.security.HTTPBearer):
    """Dependency for fastapi. Checks the authorization header is correct, controls
    the JWT provided by the user, controls the signature, decode it, fetch from the
    API database the credentials for this user, and yields an sql_api.Creds object."""
    def __init__(self, auto_error: bool = True):
        log = logging.getLogger(__name__)
        log.info("We are building the JWTBearer")
        super(depends_jwt, self).__init__(auto_error=auto_error)

    async def __call__(self, request: fastapi.Request):
        log = logging.getLogger(__name__)
        log.setLevel(logging.INFO)
        log.info("We are in da place")
        credentials: fastapi.security.HTTPAuthorizationCredentials
        try:
            credentials = await super(JWTBearer, self).__call__(request)
        except Exception as e:
            log.error("Failed super, so failed auth.")
            raise e
        if not credentials:
            log.info("There are no creds, fuck up")
            raise fastapi.HTTPException(
                status_code=403, detail="Invalid authorization code."
            )
        if not credentials.scheme == "Bearer":
            log.info("Creds are not Bearer, get out")
            raise fastapi.HTTPException(
                status_code=403, detail="Invalid authentication scheme."
            )
        token = self.verify_jwt(log, credentials.credentials)
        username = token["sub"]
        log.info(f"Greetings user {username}")
        maker = sql_api.get_maker()
        db = maker()
        try:
            log.info("Getting the user in db")
            user = sql_api.get_api_user(db, username)
        except Exception as e:
            log.error(f"Failed to get user: {e}")
            db.close()
            raise
        log.info(f"Got the user in db: {user}")
        creds = sql_api.get_creds(db, log, username)
        db.close()
        log.info(f"Got the creds: {creds}")
        yield creds

    def verify_jwt(self, log, jwtoken: str) -> dict:
        secret = config.settings["JWT_SECRET"]
        log.info(f"Secret is {secret}")
        algo = "HS256"
        log.info("Trying to decode the tokeni...")
        try:
            token = jwt.decode(jwtoken, secret, algo)
            log.info(f"Decoded token as {token}")
            now = datetime.datetime.now(datetime.timezone.utc).timestamp()
            exp = token["exp"]
            if exp < now:
                log.info(f"Token is expired now={now}, exp={exp}")
                raise fastapi.HTTPException(status_code=403, detail="Expired token")
            log.info("Token is valid")
            return token
        except Exception as e:
            log.info("Failed to decode token")
            raise e


from .get_mailbox import get_mailbox
from .get_mailboxes import get_mailboxes
from .post_token import login_for_access_token

# from .post_user import post_user

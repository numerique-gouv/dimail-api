import datetime
import logging
import typing

import fastapi
import fastapi.security
import jwt

from .. import config, sql_api
from . import err


class TokenUser(fastapi.security.HTTPBearer):
    """Dependency for fastapi. Checks the authorization header is correct, controls
    the JWT provided by the user, controls the signature, decode it, fetch from the
    API database the credentials for this user, and yields an sql_api.Creds object."""

    def __init__(self, auto_error: bool = True):
        super(TokenUser, self).__init__(auto_error=auto_error)

    async def __call__(self, request: fastapi.Request):
        log = logging.getLogger(__name__)
        log.debug("Trying to auth a user with a token")
        credentials: fastapi.security.HTTPAuthorizationCredentials
        try:
            credentials = await super(TokenUser, self).__call__(request)
        except Exception as e:
            log.info(f"Failed super raising {e}, so failed auth.")
            raise e
        if not credentials:
            log.info("There are no creds, failed auth.")
            raise err.PermissionDenied()
        if not credentials.scheme == "Bearer":
            log.info("Creds are not Bearer, failed auth.")
            raise err.PermissionDenied()
        token = self.verify_jwt(log, credentials.credentials)
        username = token["sub"]
        log.info(f"Greetings user {username}")
        maker = sql_api.get_maker()
        session = maker()
        try:
            log.info("Getting the user in db")
            user = sql_api.get_api_user(session, username)
        except Exception as e:
            log.error(f"Failed to get user: {e}")
            session.close()
            raise
        log.info(f"Got the user in db: {user}")
        # We need to keep the orm session running, to that the user object is
        # usable (he needs his orm session for some operations)
        try:
            yield user
        finally:
            session.close()

    def verify_jwt(self, log, jwtoken: str) -> dict:
        secret = config.settings["JWT_SECRET"]
        algo = "HS256"
        log.info("Trying to decode the token...")
        try:
            token = jwt.decode(jwtoken, secret, algo)
        except jwt.ExpiredSignatureError:
            log.info("Token has expired")
            raise err.PermissionDenied()
        except jwt.PyJWTError as e:
            log.info(f"Failed to decode token: {e}")
            raise err.PermissionDenied()
        except Exception as e:
            log.info(f"Unexpected <{e}>")
            raise e

        log.info(f"Decoded token as {token}")
         # TODO cette vérification est redondante
         # le jwt.decode le vérifie déjà
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        exp = token["exp"]
        if exp < now:
            log.info(f"Token is expired now={now}, exp={exp}")
            raise err.PermissionDenied()
        log.info("Token is valid")
        return token


DependsTokenUser = typing.Annotated[sql_api.DBUser, fastapi.Depends(TokenUser())]

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

    def __init__(self):
        super(TokenUser, self).__init__(auto_error=True)

    async def __call__(self, request: fastapi.Request):
        log = logging.getLogger(__name__)
        log.debug("Trying to auth a user with a token")
        credentials: fastapi.security.HTTPAuthorizationCredentials
        try:
            credentials = await super(TokenUser, self).__call__(request)
        except Exception as e:
            log.info(f"Failed super raising {e}, so failed auth.")
            raise e
        # On utilise les paramètres par défaut, et donc auto_error = True, donc
        # si on arrive ici sans exception, la variable 'credentials' est définie,
        # et le scheme est forcément "Bearer"
        assert credentials
        assert credentials.scheme == "Bearer"

        token = self.verify_jwt(log, credentials.credentials)
        username = token["sub"]
        log.info(f"Greetings user {username}")
        maker = sql_api.get_maker()
        session = maker()
        try:
            log.info("Getting the user in db")
            user = sql_api.get_user(session, username)
        except Exception as e:
            log.error(f"Failed to get user: {e}")
            session.close()
            raise e
        if not user:
            log.info("User not found in database")
            session.close()
            raise err.PermissionDenied()
        log.info(f"Got the user in db: {user}")
        # We need to keep the orm session running, so that the user object is
        # usable (it needs its orm session for some operations)
        try:
            yield user
        finally:
            session.close()

    def verify_jwt(self, log, jwtoken: str) -> dict:
        """Verify the JWT signature, decode it, and return the decoded token.
        Raises PermissionDenied if the token is invalid.

        Args:
            log: logger object
            jwtoken: the JWT token to verify

        Returns:
            dict: the decoded token

        Raises:
            PermissionDenied: if the token is invalid

        Example:
            ```python

            token = verify_jwt(log, "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTYxNjMwNjIwMH0.12z3y4x5w6v7u8t9s0r")
            ```

        See also:
            - https://pyjwt.readthedocs.io/en/stable/
            - https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

        Dependencies:
            - datetime
            - logging
            - PermissionDenied
            - config
        """
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

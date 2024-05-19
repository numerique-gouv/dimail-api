import datetime
import logging
import re
import typing
import uuid

import fastapi
import fastapi.security
import jwt

from .. import config, sql_api, sql_dovecot, web_models
from . import depends_dovecot_db, mailboxes

mail_re = re.compile("^(?P<username>[^@]+)@(?P<domain>[^@]+)$")
uuid_re = re.compile("^[0-9a-f-]{32,36}$")


class JWTBearer(fastapi.security.HTTPBearer):
    def __init__(self, auto_error: bool = True):
        log = logging.getLogger(__name__)
        log.info("We are building the JWTBearer")
        super(JWTBearer, self).__init__(auto_error=auto_error)

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


@mailboxes.get(
    "/{mailbox_id}",
    responses={
        200: {"description": "Get a mailbox from his e_mail"},
        403: {"description": "Permission denied"},
        404: {"description": "Mailbox not found"},
        422: {"description": "Email address is not well formed"},
    },
    description="The expected mailbox_id can be the e-mail address of the uuid of a mailbox",
)
async def get_mailbox(
    mailbox_id: str,
    # perms: typing.Annotated[sql_api.Creds, fastapi.Depends(get_creds)],
    perms: typing.Annotated[sql_api.Creds, fastapi.Depends(JWTBearer())],
    db: typing.Annotated[typing.Any, fastapi.Depends(depends_dovecot_db)],
    # alias_db: typing.Annotated[typing.Any, fastapi.Depends(sql_alias.get_alias_db)],
) -> web_models.Mailbox:
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.info(f"Nous cherchons qui est {mailbox_id}")
    log.info(f"Nous avons comme permissions: {perms}")
    #    test_uuid = uuid_re.match(mailbox_id)
    test_mail = mail_re.match(mailbox_id)
    #    domain = None
    #    if test_uuid is not None:
    #        print("Ca ressemble a un uuid")
    #        # We try to parse the uuid (which is good enough to match the regexp)
    #        # if it is valid, and is the uuid of an existing mailbox, we go on for this mailbox
    #        id = None
    #        try:
    #            id = uuid.UUID(mailbox_id)
    #        except:
    #            print("Je n'arrive pas a parser cet uuid")
    #            pass
    #
    #        # we do not have uuid on mailboxes yet
    #        if False: # id == mailbox.uuid:
    #            print("C'est l'uuid de la seule boite que je connais")
    #            domain = mailbox.domain
    #        else:
    #            raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    if test_mail is None:
        log.info("Ca n'a pas une tete d'adresse mail.")
        raise fastapi.HTTPException(status_code=422, detail="Invalid email address")

    log.info("Ca ressemble a une adresse mail")
    infos = test_mail.groupdict()
    domain = infos["domain"]
    username = infos["username"]
    log.info(f"Cette adresse est sur le domaine {domain}")

    if domain is None:
        log.error(
            "Comment ca le domaine n'est pas defini alors que ca match la regexp ?"
        )
        raise fastapi.HTTPException(status_code=422, detail="Invalid email address")

    if not perms.can_read(domain):
        log.info(f"Permission denied on domain {domain} for curent user")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    imap = sql_dovecot.get_dovecot_user(db, username, domain)
    if imap is None:
        log.info("La base dovecot ne contient pas cette adresse.")
        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    log.info("On a trouve l'adresse.")
    return web_models.Mailbox(
        type="mailbox",
        status="ok",
        email=imap.username + "@" + imap.domain,
        givenName=None,
        surName=None,
        displayName=None,
        username=imap.username,
        domain=imap.domain,
        uuid=uuid.uuid4(),
    )


#    if (
#        mailbox_id != "toto@example.com"
#        and mailbox_id != "d437abd5-2b49-47db-be49-05f79f1cc242"
#    ):
#        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")
#
#    return mailbox

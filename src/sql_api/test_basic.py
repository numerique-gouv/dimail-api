import pytest

from .. import sql_api
from . import database



def test_database():
    database.maker = None
    with pytest.raises(Exception) as e:
        database.get_maker()
    assert "You need to init the db by giving me a valid URL" in str(e.value)

    database.init_db("sqlite:///:memory:")

    maker = database.get_maker()
    assert maker is not None

    database.maker = None


def test_create_user(db_api_session):
    db_user = sql_api.create_user(
        db_api_session, name="toto", password="titi", is_admin=False
    )
    assert db_user == sql_api.DBUser(name="toto", is_admin=False)

    # When trying to create a user that already exists -> fail
    db_user = sql_api.create_user(db_api_session, name="toto", password="titi", is_admin=False)
    assert db_user is None

    # When trying to create a user with an invalid password -> fail
    db_user = sql_api.create_user(db_api_session, name="new", password=None, is_admin=True)
    assert db_user is None

    # When trying to create a user with an invalid is_admin -> fail
    db_user = sql_api.create_user(db_api_session, name="test", password="test", is_admin="invalid")
    assert db_user is None


def test_delete_user(db_api_session, log):
    # First, we create a user
    sql_api.create_user(db_api_session, name="toto", password="titi", is_admin=False)
    # Then, we retrieve the user
    user = sql_api.get_user(db_api_session, "toto")
    assert user == sql_api.DBUser(name="toto", is_admin=False)

    # Delete returns the user as it was before deletion, so, unchanged
    user = sql_api.delete_user(db_api_session, "toto")
    assert user == sql_api.DBUser(name="toto", is_admin=False)

    # When trying to fetch it again, we fail
    user = sql_api.get_user(db_api_session, "toto")
    assert user is None

    # when trying to delete a user that does not exist -> fail
    user = sql_api.delete_user(db_api_session, "tutu")
    assert user is None


def test_create_domain(db_api_session, log):
    db_dom = sql_api.create_domain(
        db_api_session,
        name="example.com",
        features=["webmail", "mailbox"],
    )
    assert isinstance(db_dom, sql_api.DBDomain)
    assert db_dom.name == "example.com"
    assert db_dom.features == ["webmail", "mailbox"]
    assert db_dom.webmail_domain is None
    assert db_dom.mailbox_domain is None
    assert db_dom.imap_domains is None
    assert db_dom.smtp_domains is None

    db_dom = sql_api.create_domain(
        db_api_session,
        name="domain_name",
        features=["coin", "pan"],
        webmail_domain="webmail_domain",
        mailbox_domain="mailbox_domain",
        imap_domains=["imap1", "imap2"],
        smtp_domains=["smtp1", "smtp2"],
    )
    assert isinstance(db_dom, sql_api.DBDomain)
    assert db_dom.name == "domain_name"
    assert db_dom.features == ["coin", "pan"]
    assert db_dom.webmail_domain == "webmail_domain"
    assert db_dom.mailbox_domain == "mailbox_domain"
    assert db_dom.imap_domains == ["imap1", "imap2"]
    assert db_dom.smtp_domains == ["smtp1", "smtp2"]


def test_create_user_bis(db_api_session):
    db_user = sql_api.create_user(
        db_api_session,
        name="essai-test",
        password="toto",
        is_admin=False,
    )
    assert isinstance(db_user, sql_api.DBUser)
    assert db_user.name == "essai-test"
    assert db_user.is_admin is False
    assert db_user.verify_password("toto")
    assert not db_user.verify_password("titi")


def test_update_user(db_api_session):
    db_user = sql_api.create_user(
        db_api_session,
        name="tom",
        password="toto",
        is_admin=False,
    )
    assert isinstance(db_user, sql_api.DBUser)
    assert db_user.verify_password("toto")

    db_user = sql_api.update_user_is_admin(db_api_session, "tom", True)
    assert isinstance(db_user, sql_api.DBUser)

    db_user = sql_api.get_user(db_api_session, "tom")
    assert isinstance(db_user, sql_api.DBUser)
    assert db_user.is_admin is True

    db_user = sql_api.update_user_password(db_api_session, "tom", "nouvo")
    assert isinstance(db_user, sql_api.DBUser)

    db_user = sql_api.get_user(db_api_session, "tom")
    assert isinstance(db_user, sql_api.DBUser)
    assert db_user.verify_password("nouvo")
    assert not db_user.verify_password("toto")


def test_update_user_errors(db_api_session):
    db_user = sql_api.create_user(db_api_session, "toto", "titi", False)
    assert db_user is not None

    # Je change le flag is_admin sur mon user, ça se passe bien
    db_user = sql_api.update_user_is_admin(db_api_session, "toto", True)
    assert db_user.is_admin is True

    # Je change le flag is_admin sur un user qui n'existe pas...
    db_user = sql_api.update_user_is_admin(db_api_session, "tutu", True)
    assert db_user is None

    # Je change le flag is_admin sur mon user, avec une valeur idiote
    # -> Objet inchangé, is_admin vaut toujours True (la valeur précédente)
    db_user = sql_api.update_user_is_admin(db_api_session, "toto", "idiote")
    assert db_user.is_admin is True

    # Le même test, mais avec "False" comme valeur précédente
    db_user = sql_api.update_user_is_admin(db_api_session, "toto", False)
    assert db_user.is_admin is False
    db_user = sql_api.update_user_is_admin(db_api_session, "toto", "idiote")
    assert db_user.is_admin is False

    # Je change le mot de passe d'un user qui n'existe pas -> echec
    db_user = sql_api.update_user_password(db_api_session, "tutu", "mot de passe")
    assert db_user is None

    # Je remonte mon user toto, et je stock son ancien mot de passe (haché) pour
    # vérifier que les updates échouent
    db_user = sql_api.get_user(db_api_session, "toto")
    previous = db_user.hashed_password
    db_user = sql_api.update_user_password(db_api_session, "toto", None)
    assert db_user.hashed_password == previous


def test_allows(db_api_session):
    allows = sql_api.get_allows(db_api_session, user="", domain="")
    assert allows == []

    sql_api.create_user(db_api_session, name="toto", password="toto", is_admin=False)
    sql_api.create_user(db_api_session, name="tutu", password="toto", is_admin=False)
    sql_api.create_domain(
        db_api_session,
        name="example.com",
        features=[],
    )
    sql_api.create_domain(
        db_api_session,
        name="example.net",
        features=[],
    )

    db_allow = sql_api.allow_domain_for_user(
        db_api_session,
        user="toto",
        domain="example.com",
    )
    assert isinstance(db_allow, sql_api.DBAllowed)
    assert db_allow.user == "toto"
    assert db_allow.domain == "example.com"

    db_allow = sql_api.allow_domain_for_user(
        db_api_session,
        user="toto",
        domain="example.net",
    )
    assert isinstance(db_allow, sql_api.DBAllowed)

    db_allow = sql_api.allow_domain_for_user(
        db_api_session,
        user="tutu",
        domain="example.com",
    )
    assert isinstance(db_allow, sql_api.DBAllowed)

    allows = sql_api.get_allows(db_api_session, user="toto")
    assert len(allows) == 2
    for item in allows:
        assert item.user == "toto"
        assert item.domain in ["example.com", "example.net"]

    allows = sql_api.get_allows(db_api_session, domain="example.com")
    assert len(allows) == 2
    for item in allows:
        assert item.domain == "example.com"
        assert item.user in ["toto", "tutu"]

    sql_api.deny_domain_for_user(db_api_session, "toto", "example.com")
    allows = sql_api.get_allows(db_api_session, user="toto")
    assert len(allows) == 1
    assert allows[0].user == "toto"
    assert allows[0].domain == "example.net"

    sql_api.delete_allows_by_user(db_api_session, user="toto")
    allows = sql_api.get_allows(db_api_session, user="toto")
    assert len(allows) == 0


def test_creds(db_api_session):
    user_toto = sql_api.create_user(
        db_api_session, name="toto", password="toto", is_admin=False
    )
    sql_api.create_user(db_api_session, name="tutu", password="toto", is_admin=False)
    user_admin = sql_api.create_user(
        db_api_session,
        name="chef",
        password="secret",
        is_admin=True,
    )
    sql_api.create_domain(
        db_api_session,
        name="example.com",
        features=[],
    )
    sql_api.create_domain(
        db_api_session,
        name="example.net",
        features=[],
    )

    creds = user_toto.get_creds()
    assert isinstance(creds, sql_api.Creds)
    assert creds.is_admin is False
    assert not creds.can_read("example.com")

    # Quand on donne les droits au user en SQL, ça se reflète dans les creds
    sql_api.allow_domain_for_user(db_api_session, "toto", "example.com")
    creds = user_toto.get_creds()
    assert creds.can_read("example.com")

    # Un admin n'a pas besoin de droits spécifiques
    creds = user_admin.get_creds()
    assert creds.can_read("example.com")

    # Quand on retire les droits au user en SQL, ça se reflète dans les creds
    sql_api.deny_domain_for_user(db_api_session, "toto", "example.com")
    creds = user_toto.get_creds()
    assert not creds.can_read("example.com")

    # Si on rappelle une seconde fois deny_domain_for_user, ça ne plante pas
    # Mais le domaine n'est pas trouvé dans la BDD
    data = sql_api.deny_domain_for_user(db_api_session, "toto", "example.com")
    assert data is None


def test_count_users(db_api_session):
    # Au début, il n'y a aucun utilisateur
    n = sql_api.count_users(db_api_session)
    assert n == 0

    li = sql_api.get_users(db_api_session)
    assert len(li) == 0

    # On crée un utilisateur
    user = sql_api.create_user(db_api_session, "toto", "pass", False)
    assert user is not None

    # Maintenant on a 1 utilisateur
    n = sql_api.count_users(db_api_session)
    assert n == 1

    li = sql_api.get_users(db_api_session)
    assert len(li) == 1
    assert li[0].name == "toto"

    # On crée un deuxième utilisateur
    user = sql_api.create_user(db_api_session, "toto2", "pass", False)
    assert user is not None

    # Maintenant on a 2 utilisateur
    n = sql_api.count_users(db_api_session)
    assert n == 2

    li = sql_api.get_users(db_api_session)
    assert len(li) == 2
    assert li[0].name in [ "toto", "toto2" ]
    assert li[1].name in [ "toto", "toto2" ]



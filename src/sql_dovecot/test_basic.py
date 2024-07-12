import pytest

from .. import sql_dovecot
from . import database, models


def test_database():
    database.maker = None
    with pytest.raises(Exception) as e:
        database.get_maker()
    assert "Please init the database by giving me an url..." in str(e.value)

    database.init_db("sqlite:///:memory:")

    maker = database.get_maker()
    assert maker is not None

def test_imap__create_and_get_a_user(db_dovecot_session):
    """Proves that we can create a user in dovecot db, fetch it, and checks its password."""
    imap_user = sql_dovecot.get_user(db_dovecot_session, "toto", "example.com")
    assert imap_user is None

    # On essaye de créer un user avec des valeurs idiotes -> return None
    imap_user = sql_dovecot.create_user(db_dovecot_session, None, None, None)
    assert imap_user is None

    # Le test précédent a échoué à cause du mot de passe incohérent
    # Si une ou plusieurs autre(s) valeur(s) est incohérente, le résultat sera le même.
    imap_user = sql_dovecot.create_user(db_dovecot_session, None, None, "secret")
    assert imap_user is None
    imap_user = sql_dovecot.create_user(db_dovecot_session, None, "example.com", "secret")
    assert imap_user is None
    imap_user = sql_dovecot.create_user(db_dovecot_session, "toto", None, "secret")
    assert imap_user is None

    imap_user = sql_dovecot.create_user(
        db_dovecot_session, "toto", "example.com", "secret"
    )
    assert isinstance(imap_user, sql_dovecot.ImapUser)

    imap_user = sql_dovecot.get_user(db_dovecot_session, "toto", "example.com")
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.username == "toto"
    assert imap_user.domain == "example.com"
    assert imap_user.check_password("secret")

    # Quand on supprime le user, on le récupère tel qu'il était avant suppression
    imap_user = sql_dovecot.delete_user(db_dovecot_session, "toto", "example.com")
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.username == "toto"
    assert imap_user.domain == "example.com"

    # Après qu'on l'a supprimé, le user n'existe plus.
    imap_user = sql_dovecot.get_user(db_dovecot_session, "toto", "example.com")
    assert imap_user is None

def test_delete_user(db_dovecot_session):
    # On essaye de supprimer un user qui n'existe pas
    user = sql_dovecot.delete_user(db_dovecot_session, "new", "example.com")
    assert user is None

    # On crée un user pour le test
    user = sql_dovecot.create_user(db_dovecot_session, "new", "example.com", "secret")
    assert user is not None

    # On supprime le user créé
    user = sql_dovecot.delete_user(db_dovecot_session, "new", "example.com")
    assert user is not None

def test_get_users(db_dovecot_session):
    # On teste la récupération des users d'un domaine inexistant
    # Mais ce domaine n'a encore aucun user pour le moment
    users = sql_dovecot.get_users(db_dovecot_session, "example.com")
    assert users == []

    # On ajoute un user dans le domaine
    user = sql_dovecot.create_user(db_dovecot_session, "new", "example.com", "secret")
    assert user is not None

    # On teste la récupération des users du domaine
    users = sql_dovecot.get_users(db_dovecot_session, "example.com")
    assert len(users) == 1

    # On ajoute un second user dans le domaine
    user = sql_dovecot.create_user(db_dovecot_session, "new2", "example.com", "secret")
    assert user is not None

    # On teste la récupération des users du domaine
    users = sql_dovecot.get_users(db_dovecot_session, "example.com")
    assert len(users) == 2

def test_imap__check_password():
    imap_user = models.ImapUser()
    imap_user.set_password("secret")
    assert imap_user.check_password("secret")
    assert not imap_user.check_password("wrong")

    with pytest.raises(Exception) as e:
        imap_user.password = "wrong"
        imap_user.check_password("wrong")
    assert "This password was not encoded by me, i can't check it" in str(e.value)

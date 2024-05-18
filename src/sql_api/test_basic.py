from .. import sql_api, web_models


def test_create_user(db_api):
    sql_api.create_api_user(db_api, name="toto", password="titi", is_admin=False)


def test_delete_user(db_api, log):
    log.debug("Here is a debug log")
    # First, we create a user
    sql_api.create_api_user(db_api, name="toto", password="titi", is_admin=False)
    # Then, we retrieve the user
    user = sql_api.get_api_user(db_api, "toto")
    assert user == sql_api.DBUser(name="toto", is_admin=False)
    # Delete returns the user as it was before deletion, so, unchanged
    user = sql_api.delete_api_user(db_api, "toto")
    assert user == sql_api.DBUser(name="toto", is_admin=False)
    # When trying to fetch it again, we fail
    user = sql_api.get_api_user(db_api, "toto")
    assert user == None


def test_useless():
    assert 1 == 1

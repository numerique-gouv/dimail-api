import src.sql_api.crud

def test_create_user(db):
    src.sql_api.crud.create_api_user(db, src.sql_api.schemas.ApiUser(name="toto", is_admin=False))

def test_delete_user(db, log):
    log.debug("Here is a debug log")
    # First, we create a user
    src.sql_api.crud.create_api_user(db, src.sql_api.schemas.ApiUser(name="toto", is_admin=False))
    # Then, we retrieve the user
    user = src.sql_api.crud.get_api_user(db, "toto")
    assert user == src.sql_api.models.ApiUser(name="toto", is_admin=False)
    # Delete returns the user as it was before deletion, so, unchanged
    user = src.sql_api.crud.delete_api_user(db, "toto")
    assert user == src.sql_api.models.ApiUser(name="toto", is_admin=False)
    # When trying to fetch it again, we fail
    user = src.sql_api.crud.get_api_user(db, "toto")
    assert user == None
    

def test_useless():
    assert 1 == 1

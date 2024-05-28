import pytest

from .. import utils

def test_split_email():

    (username, domain) = utils.split_email("test@example.com")
    assert username == "test"
    assert domain == "example.com"

    with pytest.raises(Exception) as e:
        (username, domain) = utils.split_email("not-an-email")
    assert str(e) == "<ExceptionInfo Exception('The email address <not-an-email> is not valid') tblen=2>"





"""This module contains the function to split an email address into its username and domain parts

Variables:
   - mail_re {re.Pattern} -- The regular expression to match an email address

Functions:
    - split_email(tuple): Split an email address into its username and domain parts
"""
import re

mail_re = re.compile("^(?P<username>[^@]+)@(?P<domain>[^@]+)$")


def split_email(email: str) -> tuple:
    """Split an email address into its username and domain parts

    Args:
        email (str): The email address to split

    Returns:
        tuple: A tuple containing the username and domain parts of the email address

    Raises:
        Exception: If the email address is not valid
    """
    test_mail = mail_re.match(email)
    if test_mail is None:
        raise Exception(f"The email address <{email}> is not valid")

    infos = test_mail.groupdict()
    domain = infos["domain"]
    username = infos["username"]

    return (username, domain)

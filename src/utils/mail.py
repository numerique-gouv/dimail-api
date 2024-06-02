import re

mail_re = re.compile("^(?P<username>[^@]+)@(?P<domain>[^@]+)$")


def split_email(email: str) -> tuple:
    test_mail = mail_re.match(email)
    if test_mail is None:
        raise Exception(f"The email address <{email}> is not valid")

    infos = test_mail.groupdict()
    domain = infos["domain"]
    username = infos["username"]

    return (username, domain)

import logging
import re
import subprocess

from .. import utils

ssh_url = None
ssh_args = None
def init_dkim_manager(url, args):
    global ssh_url
    global ssh_args
    ssh_url = url
    ssh_args = args

def make_dkim_key(selector: str, domain: str) -> (str, str):
    # opendkim-genkey -v -h sha256 -b 4096  --append-domain -s <selector> -d <domain>
    log = logging.getLogger(__name__)

    if ssh_url == "FAKE":
        pub_key = f"{selector}._domainkey.{domain}. IN TXT (" + """"v=DKIM1; h=sha256; k=rsa; "
                "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2dg8Bt0+p4EEIGF3udBpR"
                "psTd9B0UUzZPTJo64fwijJxFo8RgVUOe8vV6xzhGI22ldMAl6fYNsXih7p/AhEk+CpH"
                "QBFuittufD6Q8XyNrYMblHHfUKlkdy63Bi9v784qc1bWVI+/YRuFzEVnxQkNlbNyKFr"
                "ulZ6J/f7LR1sreSZakMHgy3ePp0QS9oUxs8tYxzWTSfnTS/VAv7"
                "GD4VoZMvLSa+u1fikagc5t3xg76P9twzBOjuFFqIFg+wPGzZZWpzSh/yfcMWHg+eLxk"
                "sxcronXnNZNnfPppNdu2Id28amHB/WB/4vqmgeM3xYIZWETDvZZIjVOzlxGtfgLuNlV"
                "LwIDAQAB"); -- This is a fake, but good enough to fool lot of people
                """
        priv_key = "This is a private key you should never see"
        return (priv_key, pub_key)
    command = [ "./make_dkim.sh", selector, domain ]
    file = subprocess.Popen(
        ["ssh"] + ssh_args + [ ssh_url, utils.make_protected_cli(command) ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    file.wait()

    if file.returncode != 0:
        log.error(f"Failed to call {command}")
        log.error(file.stdout.read())
        log.error(file.stderr.read())
        raise Exception("Failed to run ssh command")

    in_file = False
    file_name = None
    content = None
    files = {}
    for line in file.stdout:
        if in_file:
            if line == "---- EOF ----\n":
                files[file_name] = content
                in_file = False
                content = None
                file_name = None
                continue
            content = content + line
            continue
        res = re.search(r"---- FILE (.*) ----", line)
        if res:
            file_name = res.group(1)
            in_file = True
            content = ""

    return (files[f"{selector}.private"], files[f"{selector}.txt"])



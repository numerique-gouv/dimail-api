import csv
import logging
import re
import subprocess

import pydantic

from .setup import get_cluster_info

class Fake:
    # For fake clusters
    by_id: dict = {}
    by_name: dict = {}
    by_domain: dict = {}

fake = None

class OxCluster(pydantic.BaseModel):
    master_username: str = "master_user"
    master_password: str = "master_pass"
    admin_username: str = "admin_user"
    admin_password: str = "admin_pass"
    name: str = "INVALID"
    ssh_url: str | None = None
    ssh_args: list[str] = []

    def url(self):
        return self.ssh_url

    def __init__(
        self,
        name: str | None = None,
    ):
        global fake
        super().__init__()
        (name, ssh_url, ssh_args) = get_cluster_info(name)
        self.name = name
        self.ssh_url = ssh_url
        self.ssh_args = ssh_args
        if ssh_url == "FAKE":
            if fake is None:
                fake = Fake()

    def __eq__(self, other) -> bool:
        if not isinstance(other, OxCluster):
            return False
        if ( self.master_username == other.master_username and 
             self.master_password == other.master_password and
             self.name == self.name ):
            return True
        return False

    def is_fake(self) -> bool:
        if self.ssh_url == "FAKE":
            return True
        return False


class OxContext(pydantic.BaseModel):
    cid: int
    name: str
    domains: set[str]
    cluster: OxCluster
    # For fake contexts in fake clusters
    next_uid: int = 1
    by_id: dict = {}
    by_email: dict = {}
    by_username: dict = {}
    by_displayname: dict = {}

    def __eq__(self, other) -> bool:
        if not isinstance(other, OxContext):
            return False
        if other.name == self.name and other.domains == self.domains:
            return True
        return False

    @classmethod
    def read_from_csv(cls, cluster: OxCluster, line: dict):
        maps = line["lmappings"].split(",")
        cid = line["id"]
        name = line["name"]
        domains = []
        for key in maps:
            if key != cid and key != name:
                domains.append(key)
        return cls(cid=cid, name=name, domains=domains, cluster=cluster)

    def is_fake(self):
        return self.cluster.is_fake()

    def get_next_uid(self):
        self.next_uid = self.next_uid + 1
        return self.next_uid


class OxUser(pydantic.BaseModel):
    uid: int
    username: str
    givenName: str
    surName: str
    displayName: str
    email: str
    ctx: OxContext

    @classmethod
    def read_from_csv(cls, ctx: OxContext, line: dict):
        uid = line["Id"]
        username = line["Name"]
        email = line["PrimaryEmail"]
        givenName = line["Given_name"]
        surName = line["Sur_name"]
        displayName = line["Display_name"]
        return cls(
            uid=uid,
            username=username,
            email=email,
            givenName=givenName,
            surName=surName,
            displayName=displayName,
            ctx=ctx,
        )

    def is_fake(self) -> bool:
        return self.ctx.is_fake()


log = logging.getLogger("oxcli")


def _purge(self: OxCluster) -> None:
    log.info("Purge everything from the cluster")
    if self.is_fake():
        fake.by_id = {}
        fake.by_name = {}
        fake.by_domain = {}
    else:
        self.run_for_item(["/root/purge.sh"])
    log.info("Ox server is empty")


clean_text = re.compile("^[a-zA-Z0-9/.=_-]+$")


def __cmd(args: list[str]) -> str:
    clean = []
    for item in args:
        if clean_text.match(item) is not None:
            clean.append(item)
            continue
        text = "'" + item.replace("'", "\\'") + "'"
        clean.append(text)
    full = " ".join(clean)
    return full


def _run_for_csv(self: OxCluster, command: list[str]) -> list[str]:
    if self.ssh_url is None:
        raise Exception("Il faut configurer OxCluster")
    if self.is_fake():
        raise Exception("Il ne faut jamais appeler SSH sur un cluster FAKE")
    file = subprocess.Popen(
        ["ssh"] + self.ssh_args + [self.ssh_url, __cmd(command)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    reader = csv.DictReader(file.stdout)
    data = []
    for elem in reader:
        data.append(elem)
    file.wait()

    if file.returncode != 0:
        log.error(f"Failed to call {command}")
        log.error(file.stderr.read())
        raise Exception("Failed to run ssh command")

    log.info(f"We got {len(data)} csv lines from command")
    return data


def _run_for_item(self: OxCluster, command: list[str]) -> str:
    if self.ssh_url is None:
        raise Exception("Il faut configurer OxCluster")
    if self.is_fake():
        raise Exception("Il ne faut jamais appeler SSH sur un cluster FAKE")
    file = subprocess.Popen(
        ["ssh"] + self.ssh_args + [self.ssh_url, __cmd(command)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    file.wait()

    if file.returncode != 0:
        log.error(f"Failed to call {command}")
        log.error(file.stderr.read())
        raise Exception("Failed to run ssh command")

    log.info("Command success")
    return file.stdout.read()


def _list_contexts(self: OxCluster) -> [OxContext]:
    if self.is_fake():
        return list(fake.by_id.values())
    data = self.run_for_csv(
        [
            "/opt/open-xchange/sbin/listcontext",
            "-A",
            self.master_username,
            "-P",
            self.master_password,
            "--csv",
        ]
    )
    res = []
    for line in data:
        ctx = OxContext.read_from_csv(self, line)
        res.append(ctx)

    return res


def _get_context(self: OxCluster, cid: int) -> OxContext | None:
    if self.is_fake():
        cid = f"{cid}"
        if cid in fake.by_id:
            return fake.by_id[cid]
        return None
    all_contexts = self.list_contexts()
    for ctx in all_contexts:
        if ctx.cid == cid:
            return ctx
    return None


def _get_context_by_name(self: OxCluster, name: str) -> OxContext | None:
    if self.is_fake():
        if name in fake.by_name:
            return fake.by_name[name]
        return None
    all_contexts = self.list_contexts()
    for ctx in all_contexts:
        if ctx.name == name:
            return ctx
    return None


def _get_context_by_domain(self: OxCluster, domain: str) -> OxContext | None:
    if self.is_fake():
        if domain in fake.by_domain:
            return fake.by_domain[domain]
        return None
    all_contexts = self.list_contexts()
    for ctx in all_contexts:
        if domain in ctx.domains:
            return ctx
    return None

def __cmd_create_context(
    self: OxCluster,
    cid: int,
    name: str,
    domain: str,
) -> None:
    if self.is_fake():
        res = OxContext(
            cid=cid,
            name=name,
            domains=[domain],
            cluster=self,
        )
        fake.by_id[f"{cid}"] = res
        fake.by_name[name] = res
        fake.by_domain[domain] = res
        res.create_user(
            username="oxadmin",
            givenName="Admin",
            surName="Context",
            displayName="Context Admin",
            domain=domain,
        )
        user = res.by_username["oxadmin"]
        user.username="admin_user"
        res.by_username["admin_user"] = user
        res.by_username.pop("oxadmin")
        return
    self.run_for_item(
        [
            "/opt/open-xchange/sbin/createcontext",
            "-A",
            self.master_username,
            "-P",
            self.master_password,
            "--contextid",
            f"{cid}",
            "--contextname",
            name,
            "--addmapping",
            domain,
            "--quota",
            "1024",
            "--access-combination-name=groupware_standard",
            "--language=fr_FR",
            "--username",
            self.admin_username,
            "--password",
            self.admin_password,
            "--displayname",
            "Context Admin",
            "--givenname",
            "Admin",
            "--surname",
            "Context",
            "--email",
            f"oxadmin@{domain}",
        ]
    )

def _create_context(
    self: OxCluster, cid: int | None, name: str, domain: str
) -> OxContext:
    all_contexts = self.list_contexts()
    max_id = 0
    for ctx in all_contexts:
        if cid is not None and ctx.cid == cid:
            raise Exception(f"Context id {cid} already exists")
        if ctx.name == name:
            raise Exception(f"Context name {name} already exists")
        if domain in ctx.domains:
            raise Exception(
                f"Domain already {domain} " + f"mapped to context {ctx.ctx}"
            )
        if ctx.cid > max_id:
            max_id = ctx.cid
    if cid is None:
        cid = max_id + 1
    __cmd_create_context(self, cid, name, domain)
    ctx = self.get_context(cid)
    if ctx is None:
        raise Exception(
            "Created the context, but failed to list it, and with a message that is longer..."
        )
    return ctx


def _add_mapping(self: OxCluster, cid: int, domain: str) -> OxContext:
    ctx = self.get_context(cid)
    if ctx is None:
        raise Exception("Context not found")
    return ctx.add_mapping(domain)
    # data = self.run_for_item(
    #     [
    #         "/opt/open-xchange/sbin/changecontext",
    #         "-A",
    #         self.master_username,
    #         "-P",
    #         self.master_password,
    #         "--contextid",
    #         f"{cid}",
    #         "--addmapping",
    #         domain,
    #     ]
    # )
    # return self.get_context(cid)


def __add_mapping(self: OxContext, domain: str) -> OxContext:
    if self.cluster.is_fake():
        fake.by_domain[domain] = self
        self.domains.add(domain)
        return self
    self.cluster.run_for_item(
        [
            "/opt/open-xchange/sbin/changecontext",
            "-A",
            self.cluster.master_username,
            "-P",
            self.cluster.master_password,
            "--contextid",
            f"{self.cid}",
            "--addmapping",
            domain,
        ]
    )
    return self.cluster.get_context(self.cid)


def _username_exists(self: OxContext, username: str) -> bool:
    if self.is_fake():
        if username in self.by_username:
            return True
        return False
    res = self.cluster.run_for_item(
        [
            "/opt/open-xchange/sbin/existsuser",
            "-A",
            self.cluster.admin_username,
            "-P",
            self.cluster.admin_password,
            "-c",
            self.cid,
            "--username",
            username,
        ]
    )
    if "does not exist" in res:
        return False
    return True


def _displayname_exists(self: OxContext, display_name: str) -> bool:
    if self.is_fake():
        if display_name in self.by_displayname:
            return True
        return False
    res = self.cluster.run_for_item(
        [
            "/opt/open-xchange/sbin/existsuser",
            "-A",
            self.cluster.admin_username,
            "-P",
            self.cluster.admin_password,
            "-c",
            self.cid,
            "--username",
            display_name,
        ]
    )
    if "does not exists" in res:
        return False
    return True

def __cmd_create_user(
    self: OxContext,
    username: str,
    givenName: str,
    surName: str,
    displayName: str,
    email: str,
) -> None:
    if self.is_fake():
        uid = self.get_next_uid()
        user = OxUser(
            uid = uid,
            username = username,
            givenName = givenName,
            surName = surName,
            displayName = displayName,
            email = email,
            ctx = self,
        )
        self.by_id[uid] = user
        self.by_email[email] = user
        self.by_username[username] = user
        self.by_displayname[displayName] = user
        return
    self.cluster.run_for_item(
        [
            "/opt/open-xchange/sbin/createuser",
            "-A",
            self.cluster.admin_username,
            "-P",
            self.cluster.admin_password,
            "-c",
            f"{self.cid}",
            "--username",
            username,
            "--password",
            "useless",
            "--givenname",
            givenName,
            "--surname",
            surName,
            "--displayname",
            displayName,
            "--email",
            email,
            "--language",
            "fr_FR",
            "--timezone",
            "Europe/Paris",
        ]
    )

def _create_user(
    self: OxContext,
    surName: str,
    givenName: str,
    displayName: str | None = None,
    email: str | None = None,
    username: str | None = None,
    domain: str | None = None,
) -> OxUser:
    if email is None and username is not None and domain is not None:
        email = username + "@" + domain
    elif username is None and domain is None and email is not None:
        (username, domain) = email.split("@")
    else:
        raise Exception(
            "Please provide either the 'email' or both 'username' and 'domain'"
        )
    if displayName is None and givenName is not None and surName is not None:
        displayName = " ".join([givenName, surName])
    if displayName is None:
        raise Exception("displayName is mandatory")
    __cmd_create_user(self,
        username=username,
        givenName=givenName,
        surName=surName,
        displayName=displayName,
        email=email
    )
    user = self.get_user_by_name(username)
    if user is None:
        raise Exception("user seems created, but fail to get it")
    return user


def _list_users(self: OxContext) -> list[OxUser]:
    if self.is_fake():
        return list(self.by_id.values())
    data = self.cluster.run_for_csv(
        [
            "/opt/open-xchange/sbin/listuser",
            "-A",
            self.cluster.admin_username,
            "-P",
            self.cluster.admin_password,
            "-c",
            f"{self.cid}",
            "--csv",
        ]
    )
    res = []
    for line in data:
        user = OxUser.read_from_csv(self, line)
        res.append(user)
    return res


def _search_user(self: OxContext, username: str) -> list[OxUser]:
    if self.is_fake():
        if username in self.by_username:
            return [ self.by_username[username] ]
        return []
    data = self.cluster.run_for_csv(
        [
            "/opt/open-xchange/sbin/listuser",
            "-A",
            self.cluster.admin_username,
            "-P",
            self.cluster.admin_password,
            "-c",
            f"{self.cid}",
            "-s",
            username,
            "--csv",
        ]
    )
    res = []
    for line in data:
        user = OxUser.read_from_csv(self, line)
        res.append(user)
    return res


def _get_user_by_name(self: OxContext, username: str) -> OxUser | None:
    if self.is_fake():
        if username in self.by_username:
            return self.by_username[username]
        return None
    all_users = self.search_user(username)
    for user in all_users:
        if user.username == username:
            return user
    return None


def _get_user_by_email(self: OxContext, email: str) -> OxUser | None:
    if self.is_fake():
        if email in self.by_email:
            return self.by_email[email]
        return None
    all_users = self.list_users()
    for user in all_users:
        if user.email == email:
            return user
    return None


def _change_user(
    self: OxUser,
    givenName: str | None = None,
    surName: str | None = None,
    displayName: str | None = None,
) -> None:
    if self.is_fake():
        if givenName is not None:
            self.givenName = givenName
        if surName is not None:
            self.surName = surName
        if displayName is not None:
            self.ctx.by_displayname.pop(self.displayName)
            self.displayName = displayName
            self.ctx.by_displayname[displayName] = self
        return
    command = [
        "/opt/open-xchange/sbin/changeuser",
        "-A",
        self.ctx.cluster.admin_username,
        "-P",
        self.ctx.cluster.admin_password,
        "-c",
        f"{self.ctx.cid}",
        "-u",
        self.username,
    ]
    if givenName is not None:
        command.extend(["--givenname", givenName])
    if surName is not None:
        command.extend(["--surname", surName])
    if displayName is not None:
        command.extend(["--displayname", displayName])
    _ = self.ctx.cluster.run_for_item(command)


def _delete_user(
    self: OxUser
) -> None:
    if self.is_fake():
        self.ctx.by_id.pop(self.uid)
        self.ctx.by_username.pop(self.username)
        self.ctx.by_displayname.pop(self.displayName)
        self.ctx.by_email.pop(self.email)
        return
    command = [
        "/opt/open-xchange/sbin/deleteuser",
        "-A",
        self.ctx.cluster.admin_username,
        "-P",
        self.ctx.cluster.admin_password,
        "-c",
        f"{self.ctx.cid}",
        "-u",
        self.username,
    ]
    _ = self.ctx.cluster.run_for_item(command)

OxCluster.purge = _purge
OxCluster.run_for_csv = _run_for_csv
OxCluster.run_for_item = _run_for_item

OxCluster.list_contexts = _list_contexts
OxCluster.get_context = _get_context
OxCluster.get_context_by_name = _get_context_by_name
OxCluster.get_context_by_domain = _get_context_by_domain
OxCluster.create_context = _create_context
OxCluster.add_mapping = _add_mapping

OxContext.add_mapping = __add_mapping
OxContext.create_user = _create_user
OxContext.list_users = _list_users
OxContext.search_user = _search_user

OxContext.get_user_by_name = _get_user_by_name
OxContext.get_user_by_email = _get_user_by_email

OxUser.change = _change_user
OxUser.delete = _delete_user

import csv
import logging
import subprocess

import pydantic


class OxCluster(pydantic.BaseModel):
    master_username: str = "master_user"
    master_password: str = "master_pass"
    admin_username: str = "admin_user"
    admin_password: str = "admin_pass"
    ssh_url: str = "ssh://root@localhost:2222"


class OxContext(pydantic.BaseModel):
    cid: int
    name: str
    domains: set[str]
    cluster: OxCluster

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


log = logging.getLogger("oxcli")


def _purge(self: OxCluster) -> None:
    log.info("Purge everything from the cluster")
    self.run_for_item(["/root/purge.sh"])
    log.info("Ox server is empty")


def _run_for_csv(self: OxCluster, command: list[str]) -> list[dict]:
    file = subprocess.Popen(
        ["/usr/bin/ssh", self.ssh_url, " ".join(command)],
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
    file = subprocess.Popen(
        ["/usr/bin/ssh", self.ssh_url, " ".join(command)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    file.wait()

    if file.returncode != 0:
        log.error(f"Faled to call {command}")
        log.error(file.stderr.read())
        raise Exception("Failed to run ssh command")

    log.info("Command success")
    return file.stdout.read()


def _list_contexts(self: OxCluster) -> [OxContext]:
    data = self.run_for_csv([
        "/opt/open-xchange/sbin/listcontext",
        "-A", self.master_username,
        "-P", self.master_password,
        "--csv"
    ])
    res = []
    for line in data:
        ctx = OxContext.read_from_csv(self, line)
        res.append(ctx)

    return res


def _get_context(
    self: OxCluster, cid: int
) -> OxContext | None:
    all = self.list_contexts()
    for ctx in all:
        if ctx.cid == cid:
            return ctx
    return None


def _create_context(
    self: OxCluster, cid: int | None, name: str, domain: str
) -> OxContext:
    all = self.list_contexts()
    max_id = 0
    for ctx in all:
        if cid is not None and ctx.cid == cid:
            raise Exception(f"Context id {cid} already exists")
        if ctx.name == name:
            raise Exception(f"Context name {name} already exists")
        if domain in ctx.domains:
            raise Exception(f"Domain already {domain} mapped to context {ctx.ctx}")
        if ctx.cid > max_id:
            max_id = ctx.cid
    if cid is None:
        cid = max_id
    data = self.run_for_item([
        "/opt/open-xchange/sbin/createcontext",
        "-A", self.master_username,
        "-P", self.master_password,
        "--contextid", f"{cid}",
        "--contextname", name,
        "--addmapping", domain,
        "--quota", "1024",
        "--access-combination-name=groupware_standard",
        "--language=fr_FR",
        "--username", self.admin_username,
        "--password", self.admin_password,
        "--displayname", "'Context Admin'",
        "--givenname", "Admin",
        "--surname", "Context",
        "--email",
        f"oxadmin@{domain}",
    ])
    ctx = self.get_context(cid)
    if ctx is None:
        raise Exception("Created the context, but failed to list it...")
    return ctx

def _add_mapping(
    self: OxCluster, cid: int, domain: str
) -> OxContext:
    ctx = self.get_context(cid)
    if ctx is None:
        raise Exception("Context not found")
    return ctx.add_mapping(domain)
    data = self.run_for_item([
        "/opt/open-xchange/sbin/changecontext",
        "-A", self.master_username,
        "-P", self.master_password,
        "--contextid", f"{cid}",
        "--addmapping", domain
    ])
    return self.get_context(cid)

def __add_mapping(
    self: OxContext, domain: str
) -> OxContext:
    data = self.cluster.run_for_item([
        "/opt/open-xchange/sbin/changecontext",
        "-A", self.cluster.master_username,
        "-P", self.cluster.master_password,
        "--contextid", f"{self.cid}",
        "--addmapping", domain
    ])
    self = self.cluster.get_context(self.cid)
    return self

OxCluster.purge        = _purge
OxCluster.run_for_csv  = _run_for_csv
OxCluster.run_for_item = _run_for_item

OxCluster.list_contexts  = _list_contexts
OxCluster.get_context    = _get_context
OxCluster.create_context = _create_context
OxCluster.add_mapping    = _add_mapping
 
OxContext.add_mapping = __add_mapping

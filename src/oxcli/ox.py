import csv
import logging
import pydantic
import subprocess

class OxCluster(pydantic.BaseModel):
    master_username: str = 'master_user'
    master_password: str = 'master_pass'
    ssh_url: str = "ssh://root@localhost:2222"

class OxContext(pydantic.BaseModel):
    cid: int
    name: str
    domains: list[str]

    @classmethod
    def read_from_csv(cls, line: dict):
        maps = line["lmappings"].split(',')
        cid  = line["id"]
        name = line["name"]
        domains = []
        for key in maps:
            if key != cid and key != name:
                domains.append(key)
        return cls(
            cid = cid,
            name = name,
            domains = domains
        )

log = logging.getLogger('owcli')

def purge(ox_cluster: OxCluster) -> None:
    log.info("Purge everything from the cluster")
    run_for_item(ox_cluster, "/root/purge.sh")
    log.info("Ox server is empty")

def run_for_csv(ox_cluster: OxCluster, command) -> list[dict]:
    file = subprocess.Popen(
        ["/usr/bin/ssh", ox_cluster.ssh_url, command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
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

def run_for_item(ox_cluster: OxCluster, command) -> str:
    file = subprocess.Popen(
        ["/usr/bin/ssh", ox_cluster.ssh_url, command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    file.wait()

    if file.returncode != 0:
        log.error(f"Faled to call {command}")
        log.error(file.stderr.read())
        raise Exception("Failed to run ssh command")

    log.info("Command success")
    return file.stdout.read()

def list_contexts(ox_cluster: OxCluster) -> [OxContext]:
    data = run_for_csv(ox_cluster, f"/opt/open-xchange/sbin/listcontext -A {ox_cluster.master_username} -P {ox_cluster.master_password} --csv")
    res = []
    for line in data:
        res.append(OxContext.read_from_csv(line))

    return res


def create_context(ox_cluster: OxCluster, cid: int | None, name: str, domain: str) -> OxContext:
    all = list_contexts(ox_cluster)
    max_id = 0
    for ctx in all:
        if cid is not None and ctx.cid == cid:
            raise Exception(f"Context id {cid} already exists")
        if ctx.name == name:
            raise Exception(f"Context name {cid} already exists")
        if domain in ctx.domains:
            raise Exception(f"Domain already {domain} mapped to context {ctx.ctx}")
        if ctx.cid > max_id:
            max_id = ctx.cid
    if cid is None:
        cid = max_id
    data = run_for_item(ox_cluster, 
        " ".join(["/opt/open-xchange/sbin/createcontext",
            "-A", ox_cluster.master_username, "-P", ox_cluster.master_password,
            "--contextid", f"{cid}",
            "--contextname", name,
            "--addmapping", domain,
            "--quota", "1024", 
            "--access-combination-name=groupware_standard",
            "--language=fr_FR",
            "--username=admin_user",
            "--password=admin_pass",
            "--displayname", "'Context Admin'",
            "--givenname", "Admin",
            "--surname", "Context",
            "--email", f"oxadmin@{domain}"]))
    all = list_contexts(ox_cluster)
    for ctx in all:
        if ctx.cid == cid:
            log.info(f"Created context {cid}")
            return ctx
    raise Exception("Created the context, but failed to list it...")


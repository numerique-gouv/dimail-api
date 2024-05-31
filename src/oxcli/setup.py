
default_cluster = None
clusters = {}

def declare_cluster(
    name: str,
    ssh_url: str,
    ssh_args: list[str] = [],
):
    global clusters
    if name in clusters:
        raise Exception(f"Cluster {name} already declared")

    clusters[name] = {
        "url": ssh_url,
        "args": ssh_args,
    }

def set_default_cluster(name: str):
    global default_cluster
    if name not in clusters:
        raise Exception(f"Cluster {name} does not exist, it cannot be the default one")

    default_cluster = name

def get_cluster_info(name: str | None = None):
    if name is None:
        name = default_cluster

    if name not in clusters:
        raise Exception(f"The cluster {name} does not exist")

    return (name, clusters[name]["url"], clusters[name]["args"])


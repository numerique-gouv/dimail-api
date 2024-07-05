default_cluster = None
clusters = {}

old_default = None
old_clusters = {}

# Quand on veut tester les fonctions de ce fichier, il faut
# que les variables globales soient "vierges", or pytest aura
# déjà exécuté le code d'init de main.py. Alors on va faire
# semblant.
def begin_test_clusters():
    global default_cluster
    global clusters
    global old_default
    global old_clusters

    old_default = default_cluster
    old_clusters = clusters

    default_cluster = None
    clusters = {}


def end_test_clusters():
    global default_cluster
    global clusters
    global old_default
    global old_clusters

    default_cluster = old_default
    clusters = old_clusters


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
    global default_cluster
    if name is None:
        if default_cluster is None:
            raise Exception("The is no default cluster declared")
        name = default_cluster

    if name not in clusters:
        raise Exception(f"The cluster {name} does not exist")

    return (name, clusters[name]["url"], clusters[name]["args"])

"""OxCLI package. it's a module to interact with the OxCluster API.

This module provides a way to interact with the OxCluster API, to create
clusters, users, and contexts for testing purposes.

Example:
    To use the OxCLI module, you need to import the classes and functions in
    the endpoint's file.

    ```python
    from oxcli import OxCluster, OxContext, OxUser
    from oxcli import begin_test_clusters, declare_cluster, end_test_clusters
    from oxcli import get_cluster_info, set_default_cluster
    ```

    In this example, you can use the classes and functions to interact with the
    OxCluster API.

The export classes are:
    - OxCluster: class to interact with the OxCluster API
    - OxContext: class to interact with the OxCluster API
    - OxUser: class to interact

The export functions are:
    - begin_test_clusters: function to start the test clusters
    - declare_cluster: function to declare a cluster
    - end_test_clusters: function to stop the test clusters
    - get_cluster_info: function to get the cluster information
    - set_default_cluster: function to set the default cluster

__all__ = [
    OxCluster,
    OxContext,
    OxUser,
    begin_test_clusters,
    declare_cluster,
    end_test_clusters,
    get_cluster_info,
    set_default_cluster,
]
"""
from .ox import OxCluster, OxContext, OxUser
from .setup import (
    begin_test_clusters,
    declare_cluster,
    end_test_clusters,
    get_cluster_info,
    set_default_cluster,
)

__all__ = [
    OxCluster,
    OxContext,
    OxUser,
    begin_test_clusters,
    declare_cluster,
    end_test_clusters,
    get_cluster_info,
    set_default_cluster,
]

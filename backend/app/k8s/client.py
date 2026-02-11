from __future__ import annotations

from kubernetes import client
from kubernetes.client import ApiClient
from kubernetes.config.kube_config import KubeConfigLoader


def api_client_from_kubeconfig(kubeconfig_dict: dict) -> ApiClient:
    cfg = client.Configuration()
    loader = KubeConfigLoader(config_dict=kubeconfig_dict)
    loader.load_and_set(cfg)
    return ApiClient(configuration=cfg)


def core_v1(api_client: ApiClient) -> client.CoreV1Api:
    return client.CoreV1Api(api_client)


def apps_v1(api_client: ApiClient) -> client.AppsV1Api:
    return client.AppsV1Api(api_client)

PERMISSION_BY_RESOURCE_TYPE = {
    "sparkapplication": "spark.deploy",
    "kafka": "kafka.deploy",
}

NAMESPACE_ACTION_BY_RESOURCE_TYPE = {
    "sparkapplication": "spark.deploy",
    "kafka": "kafka.deploy",
}


def required_permission(resource_type: str) -> str:
    return PERMISSION_BY_RESOURCE_TYPE.get(resource_type, "k8s.write")


def required_namespace_action(resource_type: str) -> str:
    return NAMESPACE_ACTION_BY_RESOURCE_TYPE.get(resource_type, "k8s.write")

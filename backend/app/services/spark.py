from typing import Any


def build_spark_application_template(name: str, namespace: str, spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "apiVersion": "sparkoperator.k8s.io/v1beta2",
        "kind": "SparkApplication",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "type": spec.get("type", "Scala"),
            "mode": "cluster",
            "image": spec.get("image", "ghcr.io/spark:4.0.0"),
            "mainClass": spec.get("mainClass", "org.example.Main"),
            "mainApplicationFile": spec.get("mainApplicationFile", "local:///opt/spark/app.jar"),
            "driver": spec.get("driver", {"cores": 1, "memory": "1g", "serviceAccount": "default"}),
            "executor": spec.get("executor", {"cores": 1, "instances": 2, "memory": "2g"}),
            "dynamicAllocation": spec.get("dynamicAllocation", {"enabled": True}),
        },
    }

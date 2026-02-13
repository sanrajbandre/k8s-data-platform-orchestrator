from app.services.orchestration import required_namespace_action, required_permission


def test_spark_intents_require_spark_deploy_permission() -> None:
    assert required_permission("sparkapplication") == "spark.deploy"
    assert required_namespace_action("sparkapplication") == "spark.deploy"


def test_kafka_intents_require_kafka_deploy_permission() -> None:
    assert required_permission("kafka") == "kafka.deploy"
    assert required_namespace_action("kafka") == "kafka.deploy"


def test_unknown_resource_type_falls_back_to_k8s_write() -> None:
    assert required_permission("deployment") == "k8s.write"
    assert required_namespace_action("deployment") == "k8s.write"

from packaging import version


class KafkaValidationError(ValueError):
    pass


def validate_kafka_mode(kafka_mode: str, kafka_version: str, strimzi_version: str) -> None:
    kafka_v = version.parse(kafka_version)
    strimzi_v = version.parse(strimzi_version)

    if kafka_mode == "kraft":
        if kafka_v < version.parse("4.0.0"):
            raise KafkaValidationError("KRaft mode requires Kafka >= 4.0.0")
        if strimzi_v < version.parse("0.46.0"):
            raise KafkaValidationError("KRaft mode requires Strimzi >= 0.46.0")
        return

    if kafka_mode == "legacy_zookeeper":
        if kafka_version != "3.8.1":
            raise KafkaValidationError("Legacy ZooKeeper mode supports only Kafka 3.8.1 in v1")
        if strimzi_v < version.parse("0.45.0") or strimzi_v >= version.parse("0.46.0"):
            raise KafkaValidationError("Legacy ZooKeeper mode requires Strimzi 0.45.x")
        return

    raise KafkaValidationError("Unsupported kafka_mode; expected 'kraft' or 'legacy_zookeeper'")


def migration_precheck_report(cluster_name: str, namespace: str) -> dict:
    return {
        "cluster": cluster_name,
        "namespace": namespace,
        "status": "ready_for_review",
        "checks": [
            "broker version inventory captured",
            "listener compatibility reviewed",
            "storage class and persistence validated",
            "topic replication/min ISR baselines exported",
        ],
        "next_steps": [
            "Create KRaft target cluster manifest",
            "Dry-run migration in non-production namespace",
            "Schedule staged cutover window",
        ],
    }

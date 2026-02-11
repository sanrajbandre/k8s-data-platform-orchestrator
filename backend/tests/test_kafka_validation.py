import pytest

from app.services.kafka import KafkaValidationError, validate_kafka_mode


def test_kraft_accepts_kafka_4_and_strimzi_046() -> None:
    validate_kafka_mode("kraft", "4.0.0", "0.46.0")


def test_kraft_rejects_kafka_3() -> None:
    with pytest.raises(KafkaValidationError):
        validate_kafka_mode("kraft", "3.8.1", "0.46.0")


def test_legacy_accepts_381_045() -> None:
    validate_kafka_mode("legacy_zookeeper", "3.8.1", "0.45.2")


def test_legacy_rejects_kafka_4() -> None:
    with pytest.raises(KafkaValidationError):
        validate_kafka_mode("legacy_zookeeper", "4.0.0", "0.45.2")

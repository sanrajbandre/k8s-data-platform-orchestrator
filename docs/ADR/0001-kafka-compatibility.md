# ADR 0001: Kafka Compatibility Boundaries

## Decision
Support two Kafka modes:
- `kraft` for Kafka `>=4.0.0`, requiring Strimzi `>=0.46.0`.
- `legacy_zookeeper` for Kafka `3.8.1`, requiring Strimzi `0.45.x`.

## Rationale
Kafka 4.x removed ZooKeeper and Strimzi 0.46 removed ZooKeeper-based cluster support.

## Consequences
- Hard API validation on create/update.
- Legacy mode is prominently labeled and tracked for migration.

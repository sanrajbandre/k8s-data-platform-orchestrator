# Open Source Repositories Used

## Usage Policy
- We do not copy source code from external dashboard products.
- We integrate stable OSS components through public APIs, operators, and official SDKs.
- License and boundary checks are mandatory for each dependency.

## Core Repositories
| Project | Repository | License | How It Is Used |
|---|---|---|---|
| Kubernetes Python Client | https://github.com/kubernetes-client/python | Apache-2.0 | Kubernetes API integration |
| Kubeflow Spark Operator | https://github.com/kubeflow/spark-operator | Apache-2.0 | SparkApplication CR orchestration |
| Strimzi | https://github.com/strimzi/strimzi-kafka-operator | Apache-2.0 | Kafka CR orchestration |
| Prometheus | https://github.com/prometheus/prometheus | Apache-2.0 | Metrics query backend |
| Grafana | https://github.com/grafana/grafana | AGPL-3.0 | Optional dashboard integration |
| OpenTelemetry Python | https://github.com/open-telemetry/opentelemetry-python | Apache-2.0 | Telemetry instrumentation |
| FastAPI | https://github.com/fastapi/fastapi | MIT | API framework |
| React | https://github.com/facebook/react | MIT | Frontend framework |

## Not Used as Copied Product Code
- Headlamp source code
- Devtron source code

Those projects are treated as product references for capability analysis only.

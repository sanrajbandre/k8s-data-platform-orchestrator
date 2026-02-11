from dataclasses import dataclass


@dataclass
class WatchEvent:
    cluster_id: int
    namespace: str
    resource_type: str
    resource_name: str
    payload: dict

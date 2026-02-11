from dataclasses import dataclass


@dataclass
class ClusterWatcherConfig:
    cluster_id: int
    poll_seconds: int = 30


class ClusterWatcher:
    def __init__(self, config: ClusterWatcherConfig) -> None:
        self.config = config

    def run_once(self) -> dict:
        # Placeholder for informer-based synchronization.
        return {"cluster_id": self.config.cluster_id, "status": "noop"}

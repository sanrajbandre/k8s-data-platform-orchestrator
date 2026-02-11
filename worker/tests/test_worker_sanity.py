from app.watchers.cluster_watcher import ClusterWatcher, ClusterWatcherConfig


def test_cluster_watcher_noop() -> None:
    watcher = ClusterWatcher(ClusterWatcherConfig(cluster_id=1))
    result = watcher.run_once()
    assert result["status"] == "noop"

from app.services.platform_catalog import LEARNING_PATH, OSS_REPOSITORIES, platform_overview


def test_platform_overview_contains_roadmap() -> None:
    data = platform_overview()
    assert "roadmap" in data
    assert len(data["roadmap"]) >= 3


def test_oss_repositories_include_kubernetes_client() -> None:
    names = {item["name"] for item in OSS_REPOSITORIES}
    assert "Kubernetes Python Client" in names


def test_learning_path_has_ordered_phases() -> None:
    phases = [entry["phase"] for entry in LEARNING_PATH]
    assert phases == ["L1", "L2", "L3", "L4", "L5"]

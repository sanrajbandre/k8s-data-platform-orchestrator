class K8sExecutor:
    def apply_manifest(self, manifest: dict) -> dict:
        # Placeholder for server-side apply and readiness checks.
        return {"status": "applied", "kind": manifest.get("kind")}

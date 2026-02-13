from fastapi import APIRouter, Depends

from app.core.rbac import require_perm
from app.services.platform_catalog import LEARNING_PATH, OSS_REPOSITORIES, platform_overview

router = APIRouter(prefix="/platform", tags=["platform"])


@router.get("/about", dependencies=[Depends(require_perm("k8s.read"))])
def about() -> dict:
    return platform_overview()


@router.get("/oss-repositories", dependencies=[Depends(require_perm("k8s.read"))])
def oss_repositories() -> dict:
    return {
        "policy": {
            "approach": "integration-only",
            "code_copy": "forbidden",
            "note": "External OSS projects are consumed through APIs/operators/SDKs with clear license boundaries.",
        },
        "items": OSS_REPOSITORIES,
    }


@router.get("/learning-path", dependencies=[Depends(require_perm("k8s.read"))])
def learning_path() -> dict:
    return {
        "mode": "learning-with-delivery",
        "items": LEARNING_PATH,
    }

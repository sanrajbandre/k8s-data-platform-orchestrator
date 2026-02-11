from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.rbac import require_perm
from app.db.models import AuditLog

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", dependencies=[Depends(require_perm("admin.audit.read"))])
def logs(limit: int = 200, db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).all()
    return {
        "items": [
            {
                "id": r.id,
                "actor_id": r.actor_id,
                "action": r.action,
                "resource_kind": r.resource_kind,
                "resource_id": r.resource_id,
                "outcome": r.outcome,
                "ts": r.ts.isoformat(),
            }
            for r in rows
        ]
    }

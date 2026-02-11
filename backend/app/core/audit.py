from fastapi import Request
from sqlalchemy.orm import Session

from app.db.models import AuditLog, User


def append_audit(
    db: Session,
    *,
    actor: User | None,
    action: str,
    resource_kind: str,
    resource_id: str,
    diff_json: dict,
    outcome: str,
    request: Request | None = None,
) -> None:
    ip = request.client.host if request and request.client else None
    log = AuditLog(
        actor_id=actor.id if actor else None,
        action=action,
        resource_kind=resource_kind,
        resource_id=resource_id,
        diff_json=diff_json,
        outcome=outcome,
        ip=ip,
    )
    db.add(log)
    db.commit()

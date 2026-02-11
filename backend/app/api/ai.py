from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.deps import get_current_user, get_db
from app.core.rbac import require_perm
from app.db.models import AIRequest, Incident, User
from app.services.ai import AIServiceError, analyze_incident

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/incidents/{incident_id}/analyze", dependencies=[Depends(require_perm("ai.use"))])
def analyze(
    incident_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    incident = db.scalar(select(Incident).where(Incident.id == incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    try:
        data = analyze_incident(db, user_id=user.id, incident_id=incident_id, evidence=incident.evidence_json)
    except AIServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    incident.ai_summary_ref = f"ai:{incident_id}"
    db.commit()

    append_audit(
        db,
        actor=user,
        action="ai.incident.analyze",
        resource_kind="incident",
        resource_id=str(incident_id),
        diff_json={"ai_summary_ref": incident.ai_summary_ref},
        outcome="success",
        request=request,
    )
    return data


@router.get("/usage", dependencies=[Depends(require_perm("ai.use"))])
def usage(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AIRequest).order_by(AIRequest.id.desc()).limit(200)).all()
    total_cost = round(sum(r.total_cost for r in rows), 8)
    return {
        "total_cost": total_cost,
        "items": [
            {
                "id": r.id,
                "feature": r.feature,
                "model": r.model,
                "total_tokens": r.total_tokens,
                "total_cost": r.total_cost,
                "ts": r.ts.isoformat(),
            }
            for r in rows
        ],
    }


@router.get("/cost-reports", dependencies=[Depends(require_perm("ai.use"))])
def cost_reports(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(
            AIRequest.model,
            func.count(AIRequest.id).label("requests"),
            func.sum(AIRequest.total_tokens).label("tokens"),
            func.sum(AIRequest.total_cost).label("cost"),
        ).group_by(AIRequest.model)
    ).all()
    return {
        "items": [
            {
                "model": row.model,
                "requests": int(row.requests or 0),
                "tokens": int(row.tokens or 0),
                "cost": float(row.cost or 0.0),
            }
            for row in rows
        ]
    }

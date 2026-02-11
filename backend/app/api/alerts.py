from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.deps import get_current_user, get_db
from app.core.rbac import require_perm
from app.db.models import AlertRule, Incident, User
from app.db.schemas import AlertRuleCreate, AlertRuleOut, IncidentOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/rules", response_model=AlertRuleOut, dependencies=[Depends(require_perm("alerts.manage"))])
def create_rule(
    payload: AlertRuleCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AlertRuleOut:
    rule = AlertRule(
        name=payload.name,
        scope=payload.scope,
        promql=payload.promql,
        interval_sec=payload.interval_sec,
        threshold=payload.threshold,
        severity=payload.severity,
        channels=payload.channels,
        enabled=True,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    append_audit(
        db,
        actor=user,
        action="alerts.rule.create",
        resource_kind="alert_rule",
        resource_id=str(rule.id),
        diff_json={"name": rule.name, "severity": rule.severity, "channels": rule.channels},
        outcome="success",
        request=request,
    )
    return AlertRuleOut.model_validate(rule)


@router.get("/rules", response_model=list[AlertRuleOut], dependencies=[Depends(require_perm("alerts.manage"))])
def list_rules(db: Session = Depends(get_db)) -> list[AlertRuleOut]:
    rows = db.scalars(select(AlertRule).order_by(AlertRule.id.desc())).all()
    return [AlertRuleOut.model_validate(r) for r in rows]


@router.get("/incidents", response_model=list[IncidentOut], dependencies=[Depends(require_perm("alerts.manage"))])
def list_incidents(db: Session = Depends(get_db)) -> list[IncidentOut]:
    rows = db.scalars(select(Incident).order_by(Incident.id.desc())).all()
    return [IncidentOut.model_validate(i) for i in rows]


@router.post(
    "/incidents/{incident_id}/ack",
    dependencies=[Depends(require_perm("alerts.manage"))],
)
def acknowledge_incident(
    incident_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    incident = db.scalar(select(Incident).where(Incident.id == incident_id))
    if not incident:
        return {"status": "not_found"}

    incident.state = "acknowledged"
    db.commit()
    append_audit(
        db,
        actor=user,
        action="alerts.incident.ack",
        resource_kind="incident",
        resource_id=str(incident_id),
        diff_json={"state": "acknowledged"},
        outcome="success",
        request=request,
    )
    return {"status": "acknowledged"}

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.deps import get_current_user, get_db
from app.core.rbac import require_perm
from app.db.models import Permission, Role, User, UserRole
from app.db.schemas import PermissionOut, RoleOut

router = APIRouter(prefix="/rbac", tags=["rbac"])


@router.get("/roles", response_model=list[RoleOut], dependencies=[Depends(require_perm("admin.rbac.read"))])
def list_roles(db: Session = Depends(get_db)) -> list[RoleOut]:
    return [RoleOut.model_validate(r) for r in db.scalars(select(Role).order_by(Role.name)).all()]


@router.get(
    "/permissions",
    response_model=list[PermissionOut],
    dependencies=[Depends(require_perm("admin.rbac.read"))],
)
def list_permissions(db: Session = Depends(get_db)) -> list[PermissionOut]:
    rows = db.scalars(select(Permission).order_by(Permission.name)).all()
    return [PermissionOut.model_validate(p) for p in rows]


@router.post(
    "/users/{user_id}/roles/{role_id}",
    dependencies=[Depends(require_perm("admin.rbac.write"))],
)
def bind_role(
    user_id: int,
    role_id: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    user = db.scalar(select(User).where(User.id == user_id))
    role = db.scalar(select(Role).where(Role.id == role_id))
    if not user or not role:
        raise HTTPException(status_code=404, detail="User or role not found")

    exists = db.scalar(select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id))
    if exists is None:
        db.add(UserRole(user_id=user_id, role_id=role_id))
        db.commit()

    append_audit(
        db,
        actor=actor,
        action="rbac.bind_role",
        resource_kind="user_role",
        resource_id=f"{user_id}:{role_id}",
        diff_json={"user_id": user_id, "role_id": role_id},
        outcome="success",
        request=request,
    )
    return {"status": "ok"}

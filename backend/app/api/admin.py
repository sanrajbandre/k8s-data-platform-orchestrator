from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.rbac import require_perm
from app.db.models import Permission, Role, User
from app.db.schemas import PermissionOut, RoleOut, UserOut

router = APIRouter(tags=["admin"])


@router.get("/users", response_model=list[UserOut], dependencies=[Depends(require_perm("admin.users.write"))])
def list_users(db: Session = Depends(get_db)) -> list[UserOut]:
    rows = db.scalars(select(User).order_by(User.id.desc())).all()
    return [UserOut.model_validate(row) for row in rows]


@router.get("/roles", response_model=list[RoleOut], dependencies=[Depends(require_perm("admin.rbac.read"))])
def list_roles_alias(db: Session = Depends(get_db)) -> list[RoleOut]:
    rows = db.scalars(select(Role).order_by(Role.name)).all()
    return [RoleOut.model_validate(row) for row in rows]


@router.get(
    "/permissions",
    response_model=list[PermissionOut],
    dependencies=[Depends(require_perm("admin.rbac.read"))],
)
def list_permissions_alias(db: Session = Depends(get_db)) -> list[PermissionOut]:
    rows = db.scalars(select(Permission).order_by(Permission.name)).all()
    return [PermissionOut.model_validate(row) for row in rows]

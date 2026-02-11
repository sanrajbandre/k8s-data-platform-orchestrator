from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.db.models import Permission, RolePermission, UserNamespaceScope, UserRole
from app.db.models import User as UserModel


class PermissionDenied(HTTPException):
    def __init__(self, detail: str = "Permission denied") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _user_permission_set(db: Session, user_id: int) -> set[str]:
    stmt = (
        select(Permission.name)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user_id)
    )
    return {row[0] for row in db.execute(stmt).all()}


def require_perm(permission: str) -> Callable:
    def _dep(
        user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> UserModel:
        perms = _user_permission_set(db, user.id)
        if permission not in perms and "admin.all" not in perms:
            raise PermissionDenied(f"Missing permission: {permission}")
        return user

    return _dep


def enforce_namespace_access(
    db: Session,
    user: UserModel,
    cluster_id: int,
    namespace: str,
    action: str,
) -> None:
    scopes = db.scalars(
        select(UserNamespaceScope).where(
            UserNamespaceScope.user_id == user.id,
            UserNamespaceScope.cluster_id == cluster_id,
            UserNamespaceScope.namespace == namespace,
        )
    ).all()
    if not scopes:
        return

    for scope in scopes:
        denied = set(scope.denied_actions.get("actions", []))
        if action in denied:
            raise PermissionDenied("Namespace action denied")

    if any(action in set(scope.allowed_actions.get("actions", [])) for scope in scopes):
        return
    raise PermissionDenied("Namespace action not allowed")

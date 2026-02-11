from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.deps import get_current_user, get_db
from app.core.rbac import require_perm
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.db.models import Permission, RolePermission, User, UserRole
from app.db.schemas import LoginRequest, RefreshRequest, TokenPair, UserCreate, UserMe, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    user = db.scalar(select(User).where(User.username == payload.username, User.is_active.is_(True)))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        claims = decode_token(payload.refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = db.scalar(select(User).where(User.id == int(claims["sub"]), User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/logout")
def logout() -> dict:
    return {"status": "ok"}


@router.get("/me", response_model=UserMe)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserMe:
    stmt = (
        select(Permission.name)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user.id)
    )
    perms = sorted({row[0] for row in db.execute(stmt).all()})
    return UserMe(id=user.id, email=user.email, username=user.username, is_active=user.is_active, permissions=perms)


@router.post(
    "/users",
    response_model=UserOut,
    dependencies=[Depends(require_perm("admin.users.write"))],
)
def create_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> UserOut:
    existing = db.scalar(
        select(User).where((User.username == payload.username) | (User.email == payload.email))
    )
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    append_audit(
        db,
        actor=actor,
        action="user.create",
        resource_kind="user",
        resource_id=str(user.id),
        diff_json={"username": user.username, "email": user.email},
        outcome="success",
        request=request,
    )
    return UserOut.model_validate(user)

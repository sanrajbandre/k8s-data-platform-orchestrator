from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.models import Permission, Role, RolePermission, User, UserRole
from app.db.session import SessionLocal

DEFAULT_PERMISSIONS = [
    "admin.all",
    "admin.users.write",
    "admin.rbac.read",
    "admin.rbac.write",
    "admin.audit.read",
    "k8s.read",
    "k8s.write",
    "spark.deploy",
    "kafka.deploy",
    "alerts.manage",
    "ai.use",
]

ROLE_MAP = {
    "admin": DEFAULT_PERMISSIONS,
    "platform-operator": ["k8s.read", "k8s.write", "spark.deploy", "kafka.deploy", "alerts.manage", "ai.use"],
    "service-operator": ["k8s.read", "spark.deploy", "kafka.deploy", "alerts.manage"],
    "viewer": ["k8s.read"],
}


def main() -> None:
    db = SessionLocal()
    try:
        for perm_name in DEFAULT_PERMISSIONS:
            if db.scalar(select(Permission).where(Permission.name == perm_name)) is None:
                db.add(Permission(name=perm_name, description=perm_name))
        db.commit()

        perms = {p.name: p for p in db.scalars(select(Permission)).all()}

        for role_name, role_perms in ROLE_MAP.items():
            role = db.scalar(select(Role).where(Role.name == role_name))
            if role is None:
                role = Role(name=role_name, description=role_name)
                db.add(role)
                db.commit()
                db.refresh(role)

            for p_name in role_perms:
                perm = perms[p_name]
                link = db.scalar(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == perm.id,
                    )
                )
                if link is None:
                    db.add(RolePermission(role_id=role.id, permission_id=perm.id))
            db.commit()

        admin = db.scalar(select(User).where(User.username == "admin"))
        if admin is None:
            admin = User(
                email="admin@example.local",
                username="admin",
                hashed_password=get_password_hash("admin123!"),
                is_active=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        admin_role = db.scalar(select(Role).where(Role.name == "admin"))
        if admin_role:
            link = db.scalar(
                select(UserRole).where(UserRole.user_id == admin.id, UserRole.role_id == admin_role.id)
            )
            if link is None:
                db.add(UserRole(user_id=admin.id, role_id=admin_role.id))
                db.commit()
        print("Seed complete. Admin user: admin / admin123!")
    finally:
        db.close()


if __name__ == "__main__":
    main()

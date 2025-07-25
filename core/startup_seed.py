import logging

from sqlmodel import Session, select

from core.security import hash_password
from db import engine
from models.users import Role, User

logger = logging.getLogger("uvicorn.error")


def seed_admin() -> bool:
    """
    Ensure an 'admin' role exists and a default admin user.
    Returns True if a fresh admin user was created, False if it already existed.
    """
    with Session(engine) as s:
        created = False

        # role
        admin_role = s.exec(select(Role).where(Role.name == "admin")).first()
        if admin_role is None:
            admin_role = Role(name="admin")
            s.add(admin_role)
            created = True

        # user
        admin_user = s.exec(select(User).where(User.username == "admin")).first()
        if admin_user is None:
            admin_user = User(
                username="admin",
                hashed_password=hash_password("admin1234"),  # TODO: replace in prod
                is_active=True,
            )
            admin_user.roles.append(admin_role)
            s.add(admin_user)
            created = True
        elif admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)
            created = True

        if created:
            s.commit()

    return created


# call this from lifespan in main.py:
# from core.startup_seed import seed_admin
# seed_admin()

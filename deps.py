"""
Central place for FastAPI `Depends` callables:

* DB session provider (`get_session`)
* OAuth2 scheme for JWT bearer tokens
* Current-user loader (`get_current_user`)
* Role guards (`require_role`, `require_admin`)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session

from core.security import ALGORITHM, SECRET_KEY  # JWT settings
from db import get_session  # re-export DB session factory
from models.users import User  # SQLModel table for users

# ---------------- OAuth2 bearer-token scheme ---------------------------------
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)  # where clients POST credentials


# ---------------- Current-user dependency ---------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """
    Decode JWT, load the user from DB, ensure the account is active.
    Raises 401 if anything is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: int | None = payload.get("sub")
        if uid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.get(User, uid)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# ---------------- Role-based guard factory ---------------------------------
def require_role(role_name: str):
    """
    Returns a dependency that permits only users having *role_name*.
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    """

    def _role_guard(
        current_user: User = Depends(get_current_user),
    ) -> User:
        # Simple boolean flag shortcut
        if role_name == "admin" and getattr(current_user, "is_admin", False):
            return current_user

        # Many-to-many Role link check (User.roles is a list of Role objects)
        if any(r.name == role_name for r in getattr(current_user, "roles", [])):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{role_name.capitalize()} privileges required",
        )

    return _role_guard


# Ready-made admin guard for convenience
require_admin = require_role("admin")

from fastapi import APIRouter, Depends, HTTPException, Header, status, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import Session, select
from db import get_session
from core.security import hash_password, verify_password, create_access_token, decode_access_token
from models.users import User, Role
from schemas.user import UserCreate, UserRead, TokenResponse
from typing import Optional


router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ------------- Helpers -----------------------------------------

def _get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.exec(select(User).where(User.username == username)).first()

def _get_role(session: Session, name: str) -> Role:
    role = session.exec(select(Role).where(Role.name == name)).first()
    if not role:
        role = Role(name=name)
        session.add(role)
        session.commit()
        session.refresh(role)
    return role

# ------------- Endpoints -----------------------------------------
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    if _get_user_by_username(session, user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(username=user_in.username, hashed_password=hash_password(user_in.password))

    # Give every new user a default "user" role
    default_role = _get_role(session, "user")
    user.roles.append(default_role)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = _get_user_by_username(session, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


# ------------- Dependencies -----------------------------------------

async def get_current_user(token: str = Security(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    user = session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user     # Expected type 'User', got 'type[User] | None' instead

# Admin‑role guard
def require_role(role_name: str):
    def _guard(current_user: User = Depends(get_current_user)) -> User:
        if role_name not in {role.name for role in current_user.roles}:
            raise HTTPException(status_code=403, detail=f"Requires role: {role_name}")
        return current_user
    return _guard

# A ready-made guard for reuse in routes
# require_admin = require_role("admin")
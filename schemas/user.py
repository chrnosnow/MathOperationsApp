from typing import List

from pydantic import BaseModel, constr


class RoleRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6, max_length=100)


class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    roles: List[RoleRead] = []

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

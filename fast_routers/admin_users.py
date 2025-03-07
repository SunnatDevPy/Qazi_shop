from enum import Enum
from typing import Annotated, Optional

import bcrypt
from asyncpg.pgproto.pgproto import timedelta
from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Depends
from pydantic import BaseModel

from fast_routers.jwt_ import get_current_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models import AdminPanelUser

admin_user_router = APIRouter(prefix='/panel-users', tags=['Panel User'])


class Token(BaseModel):
    access_token: str
    token_type: str


class UserAdd(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    contact: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = False
    status: Optional[str] = "moderator"
    day_and_night: Optional[bool] = False


class UserList(BaseModel):
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    contact: Optional[str] = None
    is_active: Optional[bool] = False
    status: Optional[str] = None
    day_and_night: Optional[bool] = False


class UserId(BaseModel):
    id: Optional[int] = None


@admin_user_router.post("", name="Create Panel User")
async def user_add(user: Annotated[UserId, Depends(get_current_user)], user_create: Annotated[UserAdd, Form()]):
    try:
        user = await AdminPanelUser.create(**user_create.dict())
        return {'ok': True, "user": user}
    except:
        raise HTTPException(status_code=404, detail="Item not found")


@admin_user_router.get('', name="List Panel User")
async def user_list(user: Annotated[UserId, Depends(get_current_user)]) -> list[UserList]:
    users = await AdminPanelUser.all()
    return users


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    contact: Optional[str] = None
    is_active: Optional[bool] = None


@admin_user_router.get("/profile", name="Detail Panel User")
async def user_detail(user: Annotated[UserId, Depends(get_current_user)]):
    user = await AdminPanelUser.get(user.id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@admin_user_router.patch("/profile", name="Update User")
async def user_patch_update(user: Annotated[UserId, Depends(get_current_user)], items: Annotated[UserUpdate, Form()]):
    user = await AdminPanelUser.get(user.id)
    if user:
        update_data = {k: v for k, v in items.dict().items() if v is not None}
        if update_data:
            await AdminPanelUser.update(user.id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


class UserStatus(str, Enum):
    MODERATOR = "moderator"
    ADMIN = "admin"
    CALL_CENTER = "call center"


@admin_user_router.patch("/status", name="Update Status")
async def user_add(user: Annotated[UserId, Depends(get_current_user)], user_id: int,
                   status: Annotated[UserStatus, Form()]):
    operator = await AdminPanelUser.get(user_id)
    user = await AdminPanelUser.get(user_id)
    if status not in ['MODERATOR', 'moderator', 'admin', "ADMIN", 'CALL_CENTER', "call center"]:
        raise HTTPException(status_code=404, detail="Not status")
    if operator:
        if operator.status.value == "admin":
            if status == 'string' or status == '':
                status = None
            await AdminPanelUser.update(user.id, status=status)
            return {"ok": True, "user": user}
        else:
            raise HTTPException(status_code=404, detail="Bu userda xuquq yo'q")
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@admin_user_router.delete("/")
async def user_delete(operator_id: int, user_id: int):
    user = await AdminPanelUser.get(operator_id)
    if user:
        if user.status.value in ["admin", "superuser"]:
            await AdminPanelUser.delete(user_id)
            return {"ok": True, 'id': user_id}
        else:
            raise HTTPException(status_code=404, detail="Bu userda xuquq yo'q")
    else:
        raise HTTPException(status_code=404, detail="Item not found")


class UserLogin(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@admin_user_router.post(path='/login', name="Login", response_model=Token)
async def login(items: Annotated[UserLogin, Form()]):
    user = await AdminPanelUser.get_from_username(items.username)
    if user:
        if verify_password(items.password, user.password):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"user_id": str(user.id)},
                expires_delta=access_token_expires
            )
            return {"token": Token(access_token=access_token, token_type='bearer'), "user": user}
        else:
            raise HTTPException(status_code=404, detail="parol yoki usernameda hatolik")
    else:
        raise HTTPException(status_code=404, detail="parol yoki usernameda hatolik")


class Register(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    contact: Optional[str] = None
    status: UserStatus
    password: str


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


@admin_user_router.post(path='/register', name="Register")
async def register(user: Annotated[UserId, Depends(get_current_user)], items: Annotated[Register, Form()]) -> UserList:
    items.password = hash_password(items.password)
    print(items)
    user: AdminPanelUser = await AdminPanelUser.filter(AdminPanelUser.username == items.username)
    if items.status not in ['MODERATOR', 'moderator', 'admin', "ADMIN", 'CALL_CENTER', "call center"]:
        raise HTTPException(status_code=404, detail="Not status")
    if user:
        raise HTTPException(status_code=404, detail="Bunday username bor")
    else:
        users = await AdminPanelUser.create(**items.dict(), day_and_night=False, is_active=False)
        return users

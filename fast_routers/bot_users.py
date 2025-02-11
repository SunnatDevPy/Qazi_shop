from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel

from models import BotUser, AdminPanelUser

bot_user_router = APIRouter(prefix='/bot-users', tags=['Bot User'])


class UserAdd(BaseModel):
    id_: int
    first_name: str
    last_name: str
    username: Optional[str] = None
    contact: str
    is_active: Optional[bool] = False
    day_and_night: Optional[bool] = True


class UserList(BaseModel):
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    contact: Optional[str] = None
    is_active: Optional[bool] = None
    day_and_night: Optional[bool] = True


@bot_user_router.post("", name="Create Bot User")
async def user_add(operator_id: int, user_create: Annotated[UserAdd, Form()]):
    admin_user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    if admin_user:
        if admin_user.status in ['moderator', "admin"]:
            result = await BotUser.create(**user_create.dict())
            return {'ok': True, "user": result}
        else:
            raise HTTPException(status_code=404, detail="Bu userda xuquq yo'q")
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@bot_user_router.get('', name="List Bot User")
async def user_list() -> list[UserList]:
    users = await BotUser.all()
    return users


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    contact: Optional[str] = None
    is_active: Optional[bool] = None


@bot_user_router.get("/profile", name="Detail Bot User")
async def user_detail(user_id: int):
    user = await BotUser.get(user_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@bot_user_router.patch("/profile", name="Update Bot User")
async def user_patch_update(operator_id: int, items: Annotated[UserUpdate, Form()]):
    user = await BotUser.get(operator_id)
    if user and operator_id:
        update_data = {k: v for k, v in items.dict().items() if v is not None}
        if update_data:
            await BotUser.update(user.id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@bot_user_router.delete("/")
async def user_delete(operator_id: int, user_id: int):
    user = await BotUser.get(operator_id)
    if user:
        if user.status.value in ['moderator', "admin"]:
            await BotUser.delete(user_id)
            return {"ok": True, 'id': user_id}
        else:
            raise HTTPException(status_code=404, detail="Bu userda xuquq yo'q")
    else:
        raise HTTPException(status_code=404, detail="Item not found")

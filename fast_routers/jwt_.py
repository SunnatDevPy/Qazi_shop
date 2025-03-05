from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from typing import Annotated

import jwt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from icecream import icecream
from jose import JWTError
from passlib.context import CryptContext
from passlib.exc import InvalidTokenError
from pydantic import BaseModel
from starlette import status

from models import BotUser, AdminPanelUser

SECRET_KEY = "selectstalker"
ALGORITHM = "SHA256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480
REFRESH_TOKEN_EXPIRE_DAYS = 100

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
jwt_router = APIRouter()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}, )


async def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if 'exp' in payload and datetime.utcnow() > datetime.utcfromtimestamp(payload['exp']):
            raise HTTPException(status_code=401, detail="Refresh token expired")
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        new_access_token = create_access_token(data={"sub": user_id})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        icecream.ic(payload)
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await AdminPanelUser.get(int(user_id))
    if user:
        pass
    else:
        user = await BotUser.get(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


class Token(BaseModel):
    access_token: str
    token_type: str


class UserId(BaseModel):
    user_id: int


class RefreshToken(BaseModel):
    refresh_token: int


@jwt_router.post("/me/")
async def protected_route(user_id=Depends(get_current_user)):
    return {"message": f"Ruxsat berildi {user_id}"}


@jwt_router.post("/bot-token", response_model=Token)
async def login_for_access_token(user_id: Annotated[UserId, Depends()]) -> Token:
    user = await BotUser.get(user_id.user_id)
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"user_id": str(user_id.user_id)},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type='bearer')
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@jwt_router.post("/admin-token", response_model=Token)
async def login_for_access_token(user_id: Annotated[UserId, Depends()]) -> Token:
    user = await AdminPanelUser.get(user_id.user_id)
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"user_id": str(user_id.user_id)},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type='bearer')
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@jwt_router.post("/refresh")
def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = refresh_access_token(
        data={"user_id": str(user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": new_access_token, "token_type": "bearer"}

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.entities import User
from app.core.security import decode_token


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")

    token = authorization.replace("Bearer ", "", 1)
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态已失效")

    user = db.get(User, payload["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前账户已被禁用")
    return user


def get_optional_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "", 1)
    payload = decode_token(token)
    if not payload:
        return None
    user = db.get(User, payload["user_id"])
    if not user or user.status != "active":
        return None
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return user

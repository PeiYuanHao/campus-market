from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_admin
from app.db.database import get_db
from app.models.entities import Item, Message, User
from app.schemas.common import APIMessage, AdminUserListResponse, AdminUserOut, ItemListResponse, UserStatusUpdate
from app.services.serializers import item_to_schema


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    keyword: str = Query(default=""),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    del admin
    stmt = (
        select(
            User,
            func.count(Item.id).label("item_count"),
            func.sum(case((Item.status == "on_sale", 1), else_=0)).label("on_sale_count"),
        )
        .outerjoin(Item, Item.seller_id == User.id)
        .where(User.role == "student")
        .group_by(User.id)
        .order_by(User.created_at.desc())
    )
    if keyword:
        stmt = stmt.where(User.username.like(f"%{keyword}%"))

    rows = db.execute(stmt).all()
    users = [
        AdminUserOut(
            id=user.id,
            username=user.username,
            role=user.role,
            status=user.status,
            phone=user.phone,
            avatar=user.avatar,
            created_at=user.created_at,
            item_count=item_count or 0,
            on_sale_count=on_sale_count or 0,
        )
        for user, item_count, on_sale_count in rows
    ]
    return AdminUserListResponse(users=users, total=len(users))


@router.patch("/users/{user_id}/status", response_model=APIMessage)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    del admin
    if payload.status not in {"active", "disabled"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户状态不合法")

    target = db.get(User, user_id)
    if not target or target.role != "student":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="普通用户不存在")

    target.status = payload.status
    db.commit()
    return APIMessage(message="用户状态已更新")


@router.delete("/users/{user_id}", response_model=APIMessage)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    del admin
    target = db.get(User, user_id)
    if not target or target.role != "student":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="普通用户不存在")

    db.delete(target)
    db.commit()
    return APIMessage(message="用户已删除")


@router.get("/users/{user_id}/items", response_model=ItemListResponse)
def list_user_items(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    del admin
    target = db.get(User, user_id)
    if not target or target.role != "student":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="普通用户不存在")

    items = (
        db.execute(
            select(Item)
            .where(Item.seller_id == user_id)
            .options(
                joinedload(Item.seller),
                joinedload(Item.category),
                joinedload(Item.favorites),
                joinedload(Item.messages).joinedload(Message.sender),
            )
            .order_by(Item.created_at.desc())
        )
        .scalars()
        .unique()
        .all()
    )
    return ItemListResponse(items=[item_to_schema(item) for item in items], total=len(items))

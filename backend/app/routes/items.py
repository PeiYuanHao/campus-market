from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_optional_user
from app.db.database import get_db
from app.models.entities import Favorite, Item, Message, User
from app.schemas.common import (
    APIMessage,
    ItemCreate,
    ItemDetailResponse,
    ItemListResponse,
    ItemStatusUpdate,
    ItemUpdate,
    MessageCreate,
    MessageOut,
)
from app.services.serializers import item_to_schema


router = APIRouter(prefix="/api/items", tags=["items"])


def can_manage_item(user: User, item: Item) -> bool:
    return item.seller_id == user.id or user.role == "admin"


def query_items(db: Session):
    return (
        select(Item)
        .options(
            joinedload(Item.seller),
            joinedload(Item.category),
            joinedload(Item.favorites),
            joinedload(Item.messages).joinedload(Message.sender),
        )
        .order_by(Item.created_at.desc())
    )


@router.get("", response_model=ItemListResponse)
def list_items(
    keyword: str = "",
    category_id: Optional[int] = None,
    status_filter: str = Query(default="", alias="status"),
    db: Session = Depends(get_db),
):
    stmt = query_items(db)
    if not status_filter:
        stmt = stmt.where(Item.status != "off_shelf")
    if keyword:
        like_text = f"%{keyword}%"
        stmt = stmt.where(or_(Item.title.like(like_text), Item.description.like(like_text)))
    if category_id:
        stmt = stmt.where(Item.category_id == category_id)
    if status_filter:
        stmt = stmt.where(Item.status == status_filter)

    items = db.execute(stmt).scalars().unique().all()
    return ItemListResponse(items=[item_to_schema(item) for item in items], total=len(items))


@router.get("/{item_id}", response_model=ItemDetailResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    item = db.execute(query_items(db).where(Item.id == item_id)).scalars().unique().one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    is_favorited = False
    if user:
        is_favorited = (
            db.execute(
                select(Favorite).where(Favorite.user_id == user.id, Favorite.item_id == item_id)
            ).scalar_one_or_none()
            is not None
        )
    return ItemDetailResponse(
        item=item_to_schema(item),
        messages=[
            MessageOut(id=message.id, content=message.content, created_at=message.created_at, sender=message.sender)
            for message in item.messages
        ],
        is_favorited=is_favorited,
    )


@router.post("", response_model=APIMessage)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = Item(
        **payload.dict(),
        seller_id=user.id,
        updated_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    return APIMessage(message="商品发布成功")


@router.put("/{item_id}", response_model=APIMessage)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    if not can_manage_item(user, item):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能修改自己的商品")

    for field, value in payload.dict().items():
        setattr(item, field, value)
    item.updated_at = datetime.utcnow()
    db.commit()
    return APIMessage(message="商品更新成功")


@router.delete("/{item_id}", response_model=APIMessage)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    if not can_manage_item(user, item):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限删除该商品")
    db.delete(item)
    db.commit()
    return APIMessage(message="商品已删除")


@router.patch("/{item_id}/status", response_model=APIMessage)
def update_item_status(
    item_id: int,
    payload: ItemStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.status not in {"on_sale", "reserved", "sold", "off_shelf"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商品状态不合法")

    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    if not can_manage_item(user, item):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限修改该商品")

    item.status = payload.status
    item.updated_at = datetime.utcnow()
    db.commit()
    return APIMessage(message="商品状态已更新")


@router.post("/{item_id}/messages", response_model=APIMessage)
def create_message(
    item_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    db.add(Message(item_id=item_id, sender_id=user.id, content=payload.content))
    db.commit()
    return APIMessage(message="留言发送成功")

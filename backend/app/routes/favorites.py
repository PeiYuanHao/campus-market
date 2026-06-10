from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.entities import Favorite, Item, Message, User
from app.schemas.common import APIMessage, DashboardResponse, FavoriteOut
from app.services.serializers import item_to_schema


router = APIRouter(prefix="/api", tags=["favorites"])


@router.post("/favorites/{item_id}", response_model=APIMessage)
def create_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    existing = db.execute(
        select(Favorite).where(Favorite.user_id == user.id, Favorite.item_id == item_id)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已经收藏过了")

    db.add(Favorite(user_id=user.id, item_id=item_id))
    db.commit()
    return APIMessage(message="收藏成功")


@router.delete("/favorites/{item_id}", response_model=APIMessage)
def remove_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    favorite = db.execute(
        select(Favorite).where(Favorite.user_id == user.id, Favorite.item_id == item_id)
    ).scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏记录不存在")

    db.delete(favorite)
    db.commit()
    return APIMessage(message="已取消收藏")


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item_stmt = select(Item)
    if user.role != "admin":
        item_stmt = item_stmt.where(Item.seller_id == user.id)
    items = (
        db.execute(
            item_stmt
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
    favorites = (
        db.execute(
            select(Favorite)
            .where(Favorite.user_id == user.id)
            .options(
                joinedload(Favorite.item).joinedload(Item.seller),
                joinedload(Favorite.item).joinedload(Item.category),
                joinedload(Favorite.item).joinedload(Item.favorites),
                joinedload(Favorite.item).joinedload(Item.messages).joinedload(Message.sender),
            )
            .order_by(Favorite.created_at.desc())
        )
        .scalars()
        .unique()
        .all()
    )

    return DashboardResponse(
        role_scope="admin" if user.role == "admin" else "personal",
        published_count=len(items),
        on_sale_count=sum(1 for item in items if item.status == "on_sale"),
        sold_count=sum(1 for item in items if item.status == "sold"),
        reserved_count=sum(1 for item in items if item.status == "reserved"),
        off_shelf_count=sum(1 for item in items if item.status == "off_shelf"),
        favorite_count=len(favorites),
        message_count=sum(len(item.messages) for item in items),
        items=[item_to_schema(item) for item in items],
        favorites=[
            FavoriteOut(id=favorite.id, created_at=favorite.created_at, item=item_to_schema(favorite.item))
            for favorite in favorites
        ],
    )

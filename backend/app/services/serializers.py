from app.models.entities import Favorite, Item
from app.schemas.common import ItemOut


def item_to_schema(item: Item) -> ItemOut:
    return ItemOut(
        id=item.id,
        title=item.title,
        description=item.description,
        price=item.price,
        original_price=item.original_price,
        condition_level=item.condition_level,
        image_url=item.image_url,
        status=item.status,
        created_at=item.created_at,
        updated_at=item.updated_at,
        seller=item.seller,
        category=item.category,
        favorite_count=len(item.favorites),
        message_count=len(item.messages),
    )


def favorite_to_schema(favorite: Favorite):
    return {
        "id": favorite.id,
        "created_at": favorite.created_at,
        "item": item_to_schema(favorite.item),
    }

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=50)
    phone: str = ""


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    status: str
    phone: str
    avatar: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ItemCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10)
    price: float = Field(gt=0)
    original_price: float = Field(ge=0, default=0)
    condition_level: str
    image_url: str = ""
    category_id: int


class ItemUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10)
    price: float = Field(gt=0)
    original_price: float = Field(ge=0, default=0)
    condition_level: str
    image_url: str = ""
    category_id: int


class ItemStatusUpdate(BaseModel):
    status: str


class SellerSummary(BaseModel):
    id: int
    username: str
    phone: str

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class MessageOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    sender: SellerSummary

    model_config = ConfigDict(from_attributes=True)


class ItemOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    original_price: float
    condition_level: str
    image_url: str
    status: str
    created_at: datetime
    updated_at: datetime
    seller: SellerSummary
    category: CategoryOut
    favorite_count: int = 0
    message_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ItemListResponse(BaseModel):
    items: List[ItemOut]
    total: int


class FavoriteOut(BaseModel):
    id: int
    created_at: datetime
    item: ItemOut

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    role_scope: str = "personal"
    published_count: int
    on_sale_count: int
    sold_count: int
    reserved_count: int = 0
    off_shelf_count: int = 0
    favorite_count: int
    message_count: int
    items: List[ItemOut]
    favorites: List[FavoriteOut]


class AIGenerateRequest(BaseModel):
    title: str
    category_name: str
    condition_level: str
    original_price: float = 0
    expected_price: float = 0


class AIGenerateResponse(BaseModel):
    description: str
    highlights: List[str]
    suggested_price_text: str


class APIMessage(BaseModel):
    message: str


class ItemDetailResponse(BaseModel):
    item: ItemOut
    messages: List[MessageOut]
    is_favorited: bool = False


class UserStatusUpdate(BaseModel):
    status: str


class AdminUserOut(BaseModel):
    id: int
    username: str
    role: str
    status: str
    phone: str
    avatar: str
    created_at: datetime
    item_count: int = 0
    on_sale_count: int = 0


class AdminUserListResponse(BaseModel):
    users: List[AdminUserOut]
    total: int

from uuid import uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# Pydantic Models ==============================================================
class RequestBody(BaseModel):
    item_id: str
    cart_id: str


class ResponseBody(BaseModel):
    id: str | None = None


# SQLModel Models ==============================================================
class Items(SQLModel, table=True):
    id: str = Field(primary_key=True)
    item_id: int


class Item(SQLModel, table=True):
    id: int = Field(primary_key=True, foreign_key="items.item_id")
    name: str
    price: float
    quantity: int


class Carts(SQLModel, table=True):
    mac_address: str = Field(primary_key=True)
    cart_id: int


class Cart(SQLModel, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    item_uid: str = Field(foreign_key="items.id")
    item_id: int = Field(foreign_key="items.item_id")
    cart_id: str = Field(foreign_key="carts.cart_id")

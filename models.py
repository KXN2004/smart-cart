from datetime import date
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# String Enumerations ==========================================================
class Country(StrEnum):
    USA = "USA"
    FRANCE = "France"
    ITALY = "Italy"
    GERMANY = "Germany"
    JAPAN = "Japan"
    UK = "UK"
    SPAIN = "Spain"
    SWEDEN = "Sweden"
    NETHERLANDS = "Netherlands"
    SOUTH_KOREA = "South Korea"


class Category(StrEnum):
    SHIRTS = "Shirts"
    PANTS = "Pants"
    DRESSES = "Dresses"
    JACKETS = "Jackets"
    SHOES = "Shoes"
    ACCESSORIES = "Accessories"
    UNDERWEAR = "Underwear"
    ACTIVEWEAR = "Activewear"
    OUTERWEAR = "Outerwear"
    SLEEPWEAR = "Sleepwear"
    SWIMWEAR = "Swimwear"
    SOCKS = "Socks"


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


class Brand(SQLModel, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    name: str
    country: Country
    is_active: bool


class Item(SQLModel, table=True):
    id: int = Field(primary_key=True, foreign_key="items.item_id")
    name: str
    description: str | None = None
    image: str
    marked_price: float
    discounted_price: float | None = None
    quantity: int
    brand: str = Field(foreign_key="brand.id")
    category: Category
    restocked_at: date


class Transactions(SQLModel, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    name: str
    quantity: int
    sales: float
    date: date


class Carts(SQLModel, table=True):
    mac_address: str = Field(primary_key=True)
    cart_id: int


class Cart(SQLModel, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    item_uid: str = Field(foreign_key="items.id")
    item_id: int = Field(foreign_key="items.item_id")
    cart_id: str = Field(foreign_key="carts.cart_id")

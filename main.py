import base64
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Annotated

import qrcode
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import Settings, get_settings
from database import create_schema, get_session
from logger import logger as log
from models import Cart, Carts, Item, Items, RequestBody, ResponseBody, Transactions

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    await create_schema()
    yield


app = FastAPI(
    title="Smart Cart",
    description="This is a microservice used in the Smart Cart project.",
    summary="A FastAPI REST Backend for Smart Cart.",
    version="0.1.0",
    contact={
        "name": "Kevin Nadar",
        "email": "hi@itskevin.in",
    },
    lifespan=app_lifespan,
)


@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, response: StarletteHTTPException):
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return templates.TemplateResponse(
            name="404.html",
            context={"request": request},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    raise response


@app.get("/inventory", response_class=HTMLResponse)
async def list_items(
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    if request.client.host != str(settings.admin_ip):
        return templates.TemplateResponse(
            name="404.html",
            context={"request": request},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Query items with their details
    query = select(Item)
    result = await session.execute(query)
    items = result.scalars().all()

    # Render the template with the items
    return templates.TemplateResponse(
        name="items.html", context={"request": request, "items": items}
    )


@app.get("/dashboard")
async def dashboard(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
):
    # Get sales data from transactions
    query = select(Transactions)
    result = await session.execute(query)
    transactions = result.scalars().all()

    # Initialize monthly data
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    sales_data = [0] * 12
    quantity_data = [0] * 12

    # Aggregate data by month
    for transaction in transactions:
        # Assuming transaction has a date field, you'll need to add this to your model
        month_index = transaction.date.month - 1  # 0-based index
        sales_data[month_index] += transaction.sales
        quantity_data[month_index] += transaction.quantity

    datasets = [
        {
            "label": "Sales (₹)",
            "data": sales_data,
            "borderColor": "rgb(75, 192, 192)",
            "tension": 0.1,
        },
        # {
        #     "label": "Items Sold",
        #     "data": quantity_data,
        #     "borderColor": "rgb(255, 99, 132)",
        #     "tension": 0.1,
        # },
    ]

    return templates.TemplateResponse(
        name="line.html",
        context={"request": request, "months": months, "datasets": datasets},
    )


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html", {"request": request, "items": None, "error": None}
    )


@app.get("/checkout/{cart_id}", response_class=HTMLResponse)
async def checkout_cart(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    cart_id: str,
) -> HTMLResponse:
    cart = await session.execute(select(Cart).where(Cart.cart_id == cart_id))
    cart = cart.scalars().all()
    if not cart:
        return templates.TemplateResponse(
            "invalid_cart.html",
            {"request": request, "items": None, "error": "Cart not found."},
        )
    item_ids = {}
    for record in cart:
        if record.item_id in item_ids.keys():
            item_ids[record.item_id]["quantity"] += 1
        else:
            item_ids[record.item_id] = {"quantity": 1}

    items = await session.execute(select(Item).where(Item.id.in_(item_ids)))
    result = {
        item.id: {"item_id": item.id, "name": item.name, "price": item.discounted_price}
        for item in items.scalars().all()
    }
    result = [item_ids[item_id] | result[item_id] for item_id in item_ids]

    # Update item quantities in the database
    for item_data in result:
        item_id = item_data.get("item_id")
        item = await session.get(Item, item_id)
        # transaction = await session.get(Transactions, item_data.keys()[0])
        if item:
            item.quantity -= item_data["quantity"]
            session.add(item)

    # Clear the active cart items
    await session.execute(delete(Cart).where(Cart.cart_id == cart_id))

    await session.commit()

    total = sum(item["price"] * item["quantity"] for item in result)
    total += 0.18 * total

    if not result:
        return templates.TemplateResponse(
            "checkout.html",
            {
                "request": request,
                "error": "Cart not found.",
                "total": 0,
                "qr_code": None,
            },
        )

    qr_code_url = f"upi://pay?pa=kevin.nadar@paytm&pn=Smart%20Cart&tr=EZV2025021010415054093573&am={total}&cu=INR&mc=8220"

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_code_url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    qr_code_data_uri = f"data:image/png;base64,{qr_code_base64}"

    return templates.TemplateResponse(
        "checkout.html",
        {
            "request": request,
            "total": total,
            "qr_code": qr_code_data_uri,
            "error": None,
        },
    )


@app.get("/cart/{cart_id}", response_class=HTMLResponse)
async def submit_cart_id(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    cart_id: str,
) -> HTMLResponse:
    cart = await session.execute(select(Cart).where(Cart.cart_id == cart_id))
    cart = cart.scalars().all()
    if not cart:
        return templates.TemplateResponse(
            "invalid_cart.html",
            {"request": request, "items": None, "error": "Cart not found."},
        )
    item_ids = {}
    for record in cart:
        if record.item_id in item_ids.keys():
            item_ids[record.item_id]["quantity"] += 1
        else:
            item_ids[record.item_id] = {"quantity": 1}

    items = await session.execute(select(Item).where(Item.id.in_(item_ids)))
    result = {
        item.id: {"name": item.name, "price": item.discounted_price}
        for item in items.scalars().all()
    }
    result = [item_ids[item_id] | result[item_id] for item_id in item_ids]
    if not items:
        return templates.TemplateResponse(
            "cart.html",
            {"request": request, "items": None, "error": "Cart not found."},
        )

    return templates.TemplateResponse(
        "cart.html",
        {"request": request, "items": result, "cart_id": cart_id, "error": None},
    )


@app.post("/item", response_model=ResponseBody)
async def add_item(
    body: RequestBody, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    items: Items = await session.get(Items, body.item_id)
    item: Item = await session.get(Item, items.item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found!"
        )
    cart: Carts = await session.get(Carts, body.cart_id)
    existing_cart_item = await session.execute(
        select(Cart).where(Cart.item_uid == body.item_id, Cart.cart_id == cart.cart_id)
    )
    duplicate_cart_items = existing_cart_item.scalars().all()
    if len(duplicate_cart_items) >= 1:
        removed_cart_item = duplicate_cart_items[0]
        log.info(
            "Item removed",
            item=removed_cart_item.item_id,
            cart=int(removed_cart_item.cart_id),
        )
        await session.delete(duplicate_cart_items[0])
        await session.commit()
        response = ResponseBody()
        return response
    carts: Carts = await session.get(Carts, body.cart_id)
    added_cart_item = Cart(
        item_uid=items.id, item_id=items.item_id, cart_id=int(carts.cart_id)
    )
    log.info("Item added", item=added_cart_item.item_id, cart=added_cart_item.cart_id)
    session.add(added_cart_item)
    await session.commit()
    await session.refresh(added_cart_item)
    response = ResponseBody
    response.id = added_cart_item.id
    return response

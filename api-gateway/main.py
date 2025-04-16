import httpx

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title = "OverclocKart API Gateway",
    description="Route requests to the appropriate service",
    version="0.1.0",
)

## Models for valiudating the request body
class Product(BaseModel):
    name: str
    price: float

class Order(BaseModel):
    product_id: int
    quantity: int

## service urls
CATALOG_URL = "http://127.0.0.1:5001/catalog"
ORDER_URL = "http://127.0.0.1:5002/order"

# Async HTTP client
client = httpx.AsyncClient()

## routes for catalog 
@app.get('/products', response_model=list[Product])
async def list_products():
    response = await client.get(CATALOG_URL)
    response.raise_for_status()
    return response.json()

@app.post("/products", response_model=Product, status_code=201)
async def create_product(product: Product):
    response = await client.post(CATALOG_URL, json=product.model_dump()) ### product.dict() is deprecated, so using model_dump()
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

## routes for orders
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    response = await client.get(f"{ORDER_URL}/{order_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@app.post("/orders", response_model=Order, status_code=201)
async def create_order(order: Order):
    response = await client.post(ORDER_URL, json=order.model_dump()) ### order.dict() is deprecated, so using model_dump()
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


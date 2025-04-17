import httpx
import logging
import os

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, confloat, conint
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from requests import Response
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNT = Counter("gateway_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"])

# set up logging
logger = logging.getLogger("api-gateway")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(
    title = "OverclocKart API Gateway",
    description="Route requests to the appropriate service",
    version="0.1.0",
)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"-> {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"<- {request.method} {request.url.path} {response.status_code}")
        return response


## Models for validating the request body
class Product(BaseModel):
    name: str
    price: confloat(gt=0)

class Order(BaseModel):
    product_id: conint(gt=0)
    quantity: conint(gt=0)

## service urls
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog-service:5001/products")
ORDER_URL = os.getenv("ORDER_URL", "http://order-service:5002/orders")

# Async HTTP client
client = httpx.AsyncClient()

app.add_middleware(LoggingMiddleware)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    response = await call_next(request)
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)



@app.get("/health")
async def health():
    return {"status": "ok"}

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


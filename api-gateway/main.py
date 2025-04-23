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
class ProductBase(BaseModel):
    name: str
    price: confloat(gt=0)

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int

class Order(BaseModel):
    product_id: conint(gt=0)
    quantity: conint(gt=0)

## service urls
CATALOG_HOST = os.getenv("CATALOG_HOST", "127.0.0.1")
CATALOG_PORT = os.getenv("CATALOG_PORT", "5001")
ORDER_HOST   = os.getenv("ORDER_HOST",   "127.0.0.1")
ORDER_PORT   = os.getenv("ORDER_PORT",   "5002")

CATALOG_URL = f"http://{CATALOG_HOST}:{CATALOG_PORT}/catalog"
ORDER_URL   = f"http://{ORDER_HOST}:{ORDER_PORT}/order"

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
@app.get('/products', response_model=list[ProductOut])
async def list_products():
    response = await client.get(CATALOG_URL)
    response.raise_for_status()
    return response.json()

@app.post("/products", response_model=ProductOut, status_code=201)
async def create_product(product: ProductCreate):
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


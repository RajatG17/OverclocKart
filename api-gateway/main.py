import httpx
import logging
import os

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from pydantic import BaseModel, confloat, conint, Field
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from requests import Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

## JWT
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

## Status
REQUEST_COUNT = Counter("gateway_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"])

# set up logging
logger = logging.getLogger("api-gateway")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(
    title = "OverclocKart API Gateway",
    description="Route requests to the appropriate service + Auth",
    version="0.3.0", ## 0.1.0 was the first version, 0.2.0 JWT was added, 0.3.0 CORS middleware is added
)

# cors middleware
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"], # allow GET, POST, OPTIONS etc.
    allow_headers=["*"], # allow Content-Type, Authorization, etc.
)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # if request.method == "OPTIONS":
        #     return await call_next(request)
        logger.info(f"-> {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"<- {request.method} {request.url.path} {response.status_code}")
        return response

# Middleware 
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        public_paths = {
            "/health",
            "/docs", "openapi.json",
            "/auth/register", "/auth/login" ## added for auth service
        } 
       
        # Allow unauthenticated GET /products (browse catalog)
        if request.url.path.startswith("/products") and request.method == "GET":
            response = await call_next(request)
            return response    
    
        if request.url.path in public_paths:
            response = await call_next(request)
            return response

        # Expect a bearer token in the Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(401, "Missing Bearer token")
    
        token = auth_header.split(" ", 1)[1]

        # verify signature and expiration
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            print(payload)
        except JWTError:
            raise HTTPException(401, "Invalid or expired token")
    
        # Attach user and role to request state for downstreram handling
        request.state.user = payload["sub"]
        request.state.role = payload["role"]
        return await call_next(request)
    
##  Model for proxy calls
class UserIn(BaseModel):
    username: str
    password: str

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
CATALOG_HOST = os.getenv("CATALOG_HOST", "catalog-service")
CATALOG_PORT = os.getenv("CATALOG_PORT", "5001")
ORDER_HOST   = os.getenv("ORDER_HOST",   "order-service")
ORDER_PORT   = os.getenv("ORDER_PORT",   "5002")
AUTH_HOST    = os.getenv("AUTH_HOST",    "auth-service")
AUTH_PORT    = os.getenv("AUTH_PORT",    "5003")

# service urls
CATALOG_URL = f"http://{CATALOG_HOST}:{CATALOG_PORT}/catalog"
ORDER_LIST_URL   = f"http://{ORDER_HOST}:{ORDER_PORT}/orders"
ORDER_DETAIL_URL = f"http://{ORDER_HOST}:{ORDER_PORT}/order"
AUTH_URL = f"http://{AUTH_HOST}:{AUTH_PORT}"

# Async HTTP client
client = httpx.AsyncClient()

# Add Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# Role guard
def require_admin(request: Request):
    # print(request.state.role)
    if request.state.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privlege required")

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

## routes for auth registration and login
@app.post("/auth/register", status_code=201)
async def gw_register(user: UserIn):
    # Check if the user already exists        
    resp = await(client.post(f"{AUTH_URL}/register", json=user.model_dump()))
    return JSONResponse(resp.json(), status_code=resp.status_code)

@app.post("/auth/login")
async def gw_login(user: UserIn):
    resp = await(client.post(f"{AUTH_URL}/login", json=user.model_dump()))
    return JSONResponse(resp.json(), status_code=resp.status_code)

## routes for catalog 
@app.get('/products', response_model=list[ProductOut])
async def list_products():
    response = await client.get(CATALOG_URL)
    response.raise_for_status()
    return response.json()

## route for product details
@app.post("/products", dependencies=[Depends(require_admin)], response_model=ProductOut, status_code=201)
async def create_product(product: ProductCreate, request: Request):
    print(f"DEBUG: proxying to {CATALOG_URL}")

    response = await client.post(CATALOG_URL, json=product.model_dump()) ### product.dict() is deprecated, so using model_dump()
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

## routes for orders
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    response = await client.get(f"{ORDER_LIST_URL}/{order_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@app.get("/orders", response_model=list[Order])
async def list_orders(request: Request):
    user = request.state.user
    response = await client.get(
        f"{ORDER_LIST_URL}",
        headers=[("X-User", user)]
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
    
@app.post("/orders", response_model=Order, status_code=201)
async def create_order(order: Order, request: Request):
    user = request.state.user
    response = await client.post(
        ORDER_DETAIL_URL, 
        json=order.model_dump(),
        headers=[("X-User", user)]
        ) ### order.dict() is deprecated, so using model_dump()
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()



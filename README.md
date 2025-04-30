# 🖥️  OverclocKart: PC-Components Store – Microservices Demo

A full-stack, containerised demo shop that sells PC parts.  
Built to showcase distributed-systems skills: FastAPI gateway, Flask micro­services, SQLite (swap-able), Docker Compose, observability, and (soon) JWT auth.

---
## Badges
`![CI](https://github.com/RajatG17/OverclocKart/actions/workflows/ci.yml/badge.svg?branch=main)`

## ✨  Features

| Layer | Highlights |
|-------|------------|
| **API Gateway** | FastAPI, async proxying, Pydantic validation, structured logging, Swagger UI |
| **Auth Service** | FastAPI, SQLite, bcrypt hashing, JWT issuance (`/register`,`/login`) |
| **Catalog Service** | Flask + SQLAlchemy, CRUD for products |
| **Order Service** | Flask + SQLAlchemy, inter-service call to Catalog, order lifecycle |
| **Observability** | `/health` + `/metrics` endpoints, Prometheus counters, JSON logs |
| **CI-Ready** | Github Actions: Pytest on every push/PR, Docker buildx builds 4 images, pushed to GHCR, one-shot `docker-compose up` |
| **Planned Next** | mMnimal React frontend, Postgres switch |

---

## 🗺️  Architecture

```text
                ┌──────────────┐
                │   Frontend   │
                └─────┬────────┘
                      │
                      ▼
           ┌──────────────────────┐       JWT
           │      API Gateway     │<--------------┐
           │  FastAPI :5000       │               │
           └──┬──────────┬────────┘               │
    REST /products   REST /orders                 │
         │               │                        │
         ▼               ▼                        │
 ┌──────────────┐  ┌──────────────┐               │
 │ Catalog Svc  │  │ Order Svc    │               │
 │ Flask :5001  │  │ Flask :5002  │               │
 └──────────────┘  └──────────────┘               │
                      ▲                           │
                      │  verify product           │
                      └───────────────────────────┘
           JWT issue/verify  ▲
                             │
                  ┌──────────────────┐
                  │   Auth Service   │
                  │ FastAPI :5003    │
                  └──────────────────┘
```

## 🚀 Quick Start

### Prereqs
    - Docker Desktop 20.10+
    - (Optional) curl /Postman for mannual calls

### Run services
<pre>
git clone https://github.com/RajatG17/OverclocKart.git
cd OvercolcKart
# requires Docker 20.10+ and `JWT_SECRET` in .env
docker compose up --build
</pre>

### Smoke test
<pre>
# add a product
curl -X POST http://localhost:5000/products \
     -H "Content-Type: application/json" \
     -d '{"name":"GPU","price":399.99}'

# list products
curl http://localhost:5000/products

# place an order
curl -X POST http://localhost:5000/orders \
     -H "Content-Type: application/json" \
     -d '{"product_id":1,"quantity":2}'
</pre>

## 🛠️ Local Dev (no Docker)
<pre>
# Catalog service
cd catalog-service && pip install -r requirements.txt && python app.py
# Order service (set CATALOG_HOST=127.0.0.1)
cd order-service && pip install -r requirements.txt && python app.py
# Gateway (environment variables point to localhost)
cd api-gateway && pip install -r requirements.txt && uvicorn main:app --reload
</pre>

## CI/CD Pipeline

* **CI** – GitHub Actions workflow [`ci.yml`](.github/workflows/ci.yml) triggers on every push & pull-request.  
  * **Steps:** checkout → Python 3.11 setup → pip cache → Pytest smoke test → (if branch = `main`) Docker Buildx builds images for all four services and pushes them to **GitHub Container Registry**.
* **Images** – automatically tagged `:latest` and `:<commit-sha>` under `ghcr.io/<your-handle>/<repo>/{api-gateway,catalog-service,order-service,auth-service}`.
* **Runtime** – green badge at the top of this README shows pipeline status for `main`.

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `CATALOG_HOST` | `catalog-service` | DNS name seen from inside Docker |
| `CATALOG_PORT` | `5001` | Port running catalog service |
| `ORDER_HOST` | `order-service` | - |
| `ORDER_PORT` | `5002` | Port running order service |

## Tests
- Unit + itegration tests to be implemented.

## 📈 Observability

| Service | Health | Metrics |
|---------|--------|---------|
| Gateway | `GET /health` | `GET /metrics` |
| Catalog | `GET /health` | `GET /metrics` |
| Order | `GET /health` | `GET /metrics` |

## Roadmap
1. Auth Service(JWT) & Gateway RBAC ✅
2. React + tailwind storefront
3. PostgreSQL swap
4. Github Actions CI -> Docker Hub ✅



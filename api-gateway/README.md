# API Gateway

The FastAPI gateway service toutes '/products' to the Catalof service (port 5001)
and '/orders' to the order service (port 5002).

## Setup 

```bash
cd api-gateway
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt
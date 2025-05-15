import httpx, pytest

BASE = "http://localhost:8000"

def test_full_flow():
    client = httpx.Client()

    # Register admin & customer
    resp = client.post(f"{BASE}/auth/register", json={"username":"admin", "password":"pw", "role":"admin"})
    assert resp.status_code == 201

    resp = client.post(f"{BASE}/auth/register", json={"username":"bob", "password":"pw"})
    assert resp.status_code == 201

    # Login both users
    admin_tok = client.post(f"{BASE}/auth/login", json={"username":"admin", "password":"pw"}).json()['access_token']
    cust_tok = client.post(f"{BASE}/auth/login", json={"username":"bob", "password":"pw"})

    # adding a product by admin

    headers = {"Authorization": f"Bearer {admin_tok}"}
    prod = {"name":"SSD", "price":129.99}
    resp = client.post(f"{BASE}/products", json=prod, headers=headers)
    assert resp.status_code == 201
    prod_id = resp.json()["id"]

    # customer lists products(list)
    resp = client.get(f"{BASE}/products")
    assert resp.status_code == 200
    assert any(p["id"]==prod_id for p in resp.json())

    # placing an order
    headers = {"Authorization": f"Bearer {cust_tok}"}
    order_body = {"product_id": prod_id, "quantity": 2}
    resp = client.post(f"{BASE}/orders", json=order_body, headers=headers)
    assert resp.status_code == 201
    order_id = resp.json()["id"]

    # customer fetches order history
    resp = client.get(f"{BASE}/orders", headers=headers)
    assert resp.status_code == 200
    orders = resp.json()
    assert any(o["id"]==order_id for o in orders)

    # fetch single order
    resp = client.get(f"{BASE}/orders", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["product_id"] == prod_id

import os, time, subprocess
import pytest
import httpx

COMPOSE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../docker-compose.yml"))
BASE_API = "http://localhost:5000"

@pytest.fixture(scope="session", autouse=True)
def stack():
    # 1. Spin up full stack
    up = subprocess.Popen(["docker compose", "-f", COMPOSE_FILE, "up", "--build"], stdout=subprocess.DEVNULL)
    # 2. Wait for health endpoints
    client = httpx.Client()
    for _ in range(30):
        try:
            r = client.get(f"{BASE_API}/health", timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(1)
    else:
        pytest.skip("Stack did not start in time")
    yield

    # 3. Tear down
    subprocess.Popen(["docker compose", "-f", COMPOSE_FILE, "down"], stdout=subprocess.DEVNULL)
    
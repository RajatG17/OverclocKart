import httpx, os, subprocess, signal, time

def test_gateway_health(tmp_path):
    # start only gtaeway
    proc = subprocess.Popen(
        ["python", "api-gateway/main.py"],
        env={**os.environ, "JWT_SECRET": "testsecret"},
    )
    time.sleep(5) # wait for the server to start

    try:
        r = httpx.get("http://localhost:5000/health")
        assert r.status_code == 200
    finally:
        proc.kill()
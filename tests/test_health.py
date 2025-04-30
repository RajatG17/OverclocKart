import httpx, os, subprocess, signal, time

def test_gateway_health():
    proc = subprocess.Popen(
        ["uvicorn", "api_gateway.main:app", "--port", "5000"],
        env={**os.environ, "JWT_SECRET": "testsecret"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        time.sleep(2)       
        r = httpx.get("http://127.0.0.1:5000/health", timeout=5)
        assert r.status_code == 200
    finally:
        proc.send_signal(signal.SIGINT)
        proc.wait()
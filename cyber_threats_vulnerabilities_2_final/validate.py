"""Run fixture-only HTTP smoke and a bounded legacy security suite."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def dashboard():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    with subprocess.Popen(
        [sys.executable, str(HERE / "dashboard.py"), "--port", str(port)],
        stdout=subprocess.DEVNULL,
    ) as process:
        try:
            url = f"http://127.0.0.1:{port}"
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            for _ in range(100):
                try:
                    with opener.open(url + "/healthz", timeout=0.5) as result:
                        assert result.read() == b"ok"
                    break
                except (urllib.error.URLError, TimeoutError) as error:
                    last_error = repr(error)
                    time.sleep(0.1)
            else:
                raise RuntimeError(f"Dashboard did not become ready: {last_error}")
            with opener.open(url, timeout=2) as result:
                html = result.read().decode()
                assert result.status == 200
                assert "default-src 'none'" in result.headers["Content-Security-Policy"]
                assert "1 unique normalized items" in html
                assert html.count("unavailable, 0 items") == 3
                assert html.count("<meter") == 4
            print("PASS: loopback /healthz, HTTP dashboard, fixture metrics, CSP", flush=True)
        finally:
            process.terminate()

def legacy_controls():
    runner = ROOT / "derexi-policy-pilot/backend/tests/test_security_controls.py"
    guard = """
import runpy, socket, sys
def denied(*args, **kwargs):
    raise RuntimeError('Network denied by coursework test wrapper')
original_connect = socket.socket.connect
def guarded_connect(self, address):
    if isinstance(address, tuple) and address[0] in ("127.0.0.1", "::1"):
        return original_connect(self, address)
    return denied()
socket.socket.connect = guarded_connect
socket.socket.connect_ex = denied
socket.getaddrinfo = denied
runpy.run_path(sys.argv[1], run_name='__main__')
"""
    env = dict(os.environ, DATABASE_URL="sqlite:///ctv2-tripwire.sqlite",
               PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
               SECURITY_EVIDENCE=str(HERE / "control-results.json"))
    with (HERE / "control-bounded.txt").open("wb") as log:
        try:
            result = subprocess.run([sys.executable, "-u", "-c", guard, str(runner)],
                                    env=env, stdout=log, stderr=subprocess.STDOUT, timeout=20)
            print(f"Isolated legacy suite exit: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("Isolated legacy suite timed out after 20 seconds. No final count claimed.")

if __name__ == "__main__":
    dashboard()
    legacy_controls()



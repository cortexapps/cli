"""Minimal echo server for testing Axon relay workflows."""

import json
import os
import re
import threading
import time
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

CORTEX_API_KEY = os.environ.get("CORTEX_API_KEY", "")
CORTEX_BASE_URL = os.environ.get("CORTEX_BASE_URL", "https://api.getcortexapp.com")


def wait_for_paused(callback_url, timeout=30):
    """Poll the workflow run until the action is PAUSED (ready for callback)."""
    # Extract workflow cid and run info from callback URL
    # Format: /api/v1/workflows/<cid>/callback/<encoded>
    match = re.search(r"/workflows/([^/]+)/callback/([^/?]+)", callback_url)
    if not match:
        print(f"Could not parse callback URL, waiting 5s", flush=True)
        time.sleep(5)
        return True

    workflow_cid = match.group(1)
    encoded_info = match.group(2)

    # Decode base64 to get runId#actionSlug
    import base64
    try:
        decoded = base64.b64decode(encoded_info).decode()
        run_id = decoded.split("#")[0]
    except Exception:
        print(f"Could not decode callback info, waiting 5s", flush=True)
        time.sleep(5)
        return True

    headers = {}
    if CORTEX_API_KEY:
        headers["Authorization"] = f"Bearer {CORTEX_API_KEY}"

    run_url = f"{CORTEX_BASE_URL}/api/v1/workflows/{workflow_cid}/runs/{run_id}"
    deadline = time.time() + timeout

    while time.time() < deadline:
        req = urllib.request.Request(run_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                status = data.get("status", "")
                if status == "PAUSED":
                    print(f"Workflow is PAUSED, sending callback", flush=True)
                    return True
                print(f"Workflow status: {status}, waiting...", flush=True)
        except Exception as e:
            print(f"Status check failed: {e}", flush=True)
        time.sleep(1)

    print(f"Timed out waiting for PAUSED status", flush=True)
    return False


def send_callback(callback_url, timestamp):
    """Send callback to Cortex after the action reaches PAUSED state."""
    if not wait_for_paused(callback_url):
        return

    cb_headers = {"Content-Type": "application/json"}
    if CORTEX_API_KEY:
        cb_headers["Authorization"] = f"Bearer {CORTEX_API_KEY}"

    # First: send update with output data
    update_payload = json.dumps({
        "status": "update",
        "message": "Echo server received the request",
        "response": {
            "echo_server": "axon-echo",
            "timestamp": timestamp,
            "message": "Hello from the echo server behind the Axon relay!",
        }
    }).encode()
    req1 = urllib.request.Request(
        callback_url, data=update_payload, headers=cb_headers, method="POST",
    )
    try:
        with urllib.request.urlopen(req1, timeout=10) as resp:
            print(f"Callback update: {resp.status}", flush=True)
    except Exception as e:
        print(f"Callback update failed: {e}", flush=True)

    # Second: mark as success to complete the workflow (include response for result.output)
    success_payload = json.dumps({
        "status": "success",
        "message": "Echo completed successfully",
        "response": {
            "echo_server": "axon-echo",
            "timestamp": timestamp,
            "message": "Hello from the echo server behind the Axon relay!",
        }
    }).encode()
    req2 = urllib.request.Request(
        callback_url, data=success_payload, headers=cb_headers, method="POST",
    )
    try:
        with urllib.request.urlopen(req2, timeout=10) as resp:
            print(f"Callback success: {resp.status}", flush=True)
    except Exception as e:
        print(f"Callback success failed: {e}", flush=True)


class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._respond(200, {"status": "ok", "method": "GET", "path": self.path})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length else ""

        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        callback_url = params.get("callbackURL", [None])[0]

        timestamp = datetime.now(timezone.utc).isoformat()
        result = {
            "status": "ok",
            "method": "POST",
            "path": parsed.path,
            "timestamp": timestamp,
            "received_body": body,
        }

        # Respond immediately, then call back in background
        self._respond(200, result)

        if callback_url:
            threading.Thread(
                target=send_callback, args=(callback_url, timestamp), daemon=True
            ).start()

    def _respond(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), EchoHandler)
    print("Echo server listening on :8080", flush=True)
    server.serve_forever()

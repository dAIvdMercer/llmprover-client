"""API wrapper with auth, retries, and styled error/result handling."""
import requests
import time
from IPython.display import display, HTML, clear_output


class ApiClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

    def call(self, method: str, path: str, payload: dict = None, retries: int = 2) -> dict:
        """Make an API call with retries. Returns {ok, data, error, status, latency_ms}."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        for attempt in range(retries + 1):
            try:
                start = time.time()
                r = requests.request(method, url, headers=self.headers, json=payload, timeout=30)
                latency_ms = int((time.time() - start) * 1000)
                if r.status_code in (200, 202):
                    return {"ok": True, "data": r.json(), "status": r.status_code, "latency_ms": latency_ms}
                elif r.status_code == 429 and attempt < retries:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"message": r.text}
                    return {"ok": False, "error": body.get("error", body.get("message", "Unknown error")), "status": r.status_code, "latency_ms": latency_ms}
            except requests.exceptions.Timeout:
                if attempt < retries:
                    continue
                return {"ok": False, "error": "Request timed out. Try again.", "status": 0, "latency_ms": 0}
            except Exception as e:
                return {"ok": False, "error": str(e), "status": 0, "latency_ms": 0}

    def run_async(self, endpoint: str, body: dict, timeout: int = 120, poll_interval: int = 2) -> dict:
        """Submit async job, poll with spinner, return result.

        Returns {ok, data, error, status, latency_ms} -- same shape as call().
        Pre-flight rejections (400/402/403/429) return instantly.
        """
        resp = self.call("POST", endpoint, payload=body)

        # Pre-flight rejection -- no job created
        if not resp["ok"]:
            return resp

        job_id = resp["data"].get("job_id")
        if not job_id:
            # Synchronous response (endpoint didn't use async pattern)
            return resp

        # Poll with spinner
        start = time.time()
        display(HTML('<div style="padding:8px;color:#888;">Working...</div>'))
        while (time.time() - start) < timeout:
            time.sleep(poll_interval)
            poll = self.call("GET", f"/jobs/{job_id}")

            if not poll["ok"]:
                clear_output(wait=True)
                return poll

            status = poll["data"].get("status")
            if status == "complete":
                clear_output(wait=True)
                elapsed_ms = int((time.time() - start) * 1000)
                return {"ok": True, "data": poll["data"]["result"], "status": 200, "latency_ms": elapsed_ms}
            elif status == "failed":
                clear_output(wait=True)
                return {"ok": False, "error": poll["data"].get("error", "Job failed"), "status": 500, "latency_ms": 0}

        clear_output(wait=True)
        return {"ok": False, "error": f"Timeout after {timeout}s (job_id: {job_id})", "status": 0, "latency_ms": 0}

    def health_check(self) -> bool:
        """Check API connectivity."""
        result = self.call("GET", "/health")
        return result["ok"] and result.get("data", {}).get("status") == "ok"

    def get_usage(self) -> dict:
        """Get usage data."""
        return self.call("GET", "/usage")

"""API wrapper with auth, retries, and styled error/result handling."""
import requests
import time


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
                if r.status_code == 200:
                    return {"ok": True, "data": r.json(), "status": 200, "latency_ms": latency_ms}
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

    def health_check(self) -> bool:
        """Check API connectivity."""
        result = self.call("GET", "/health")
        return result["ok"] and result.get("data", {}).get("status") == "ok"

    def get_usage(self) -> dict:
        """Get usage data."""
        return self.call("GET", "/usage")

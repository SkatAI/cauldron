"""HTTP health checks for DO apps."""

import time

import requests


def check_app_health(name: str, url: str, timeout: int = 10) -> dict:
    """Check if an app is reachable via HTTP GET.

    Args:
        name: Display name of the app
        url: Public URL to check
        timeout: Request timeout in seconds

    Returns:
        Dict with name, url, status ("ok"|"down"), http_code, response_time_ms, and error.
    """
    try:
        start = time.monotonic()
        resp = requests.get(url, timeout=timeout)
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)

        if resp.status_code == 200:
            return {
                "name": name,
                "url": url,
                "status": "ok",
                "http_code": resp.status_code,
                "response_time_ms": elapsed_ms,
                "error": None,
            }
        else:
            return {
                "name": name,
                "url": url,
                "status": "down",
                "http_code": resp.status_code,
                "response_time_ms": elapsed_ms,
                "error": f"HTTP {resp.status_code}",
            }
    except Exception as exc:
        return {
            "name": name,
            "url": url,
            "status": "down",
            "http_code": None,
            "response_time_ms": None,
            "error": str(exc),
        }

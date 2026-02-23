"""Supabase connectivity check."""

import time

import requests


def check_supabase(url: str, service_role_key: str, timeout: int = 10) -> dict:
    """Check Supabase availability via the REST API.

    Args:
        url: Supabase project URL (e.g. https://xxx.supabase.co)
        service_role_key: Supabase service role key (needed for /rest/v1/ schema access)
        timeout: Request timeout in seconds

    Returns:
        Dict with status ("ok"|"down"), response_time_ms, and optional error.
    """
    endpoint = f"{url.rstrip('/')}/rest/v1/"
    try:
        start = time.monotonic()
        resp = requests.get(
            endpoint,
            headers={
                "apikey": service_role_key,
                "Authorization": f"Bearer {service_role_key}",
            },
            timeout=timeout,
        )
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)

        if resp.status_code == 200:
            return {"status": "ok", "response_time_ms": elapsed_ms, "error": None}
        else:
            return {
                "status": "down",
                "response_time_ms": elapsed_ms,
                "error": f"HTTP {resp.status_code}",
            }
    except Exception as exc:
        return {"status": "down", "response_time_ms": None, "error": str(exc)}

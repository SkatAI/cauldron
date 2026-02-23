#!/usr/bin/env python3
"""SkatAI stack monitoring script.

Checks component health and sends Telegram alerts when something is wrong.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from checks.health import check_app_health
from checks.supabase import check_supabase
from alerts.telegram import format_alert_message, send_telegram_alert

# Apps to health-check: (name, env var for URL)
APPS = [
    ("sociosim-bff", "https://sociosim-bff-avp2t.ondigitalocean.app"),
    ("cauldron", "https://orca-app-dj9l6.ondigitalocean.app/docs"),
    ("sociosim-adk-agent", "https://sociosim-adk-e4hi9.ondigitalocean.app/docs"),
]


def _load_env():
    """Load environment variables from .env.local (local dev) or rely on system env."""
    # Try .env.local first (local dev), then .env
    env_local = Path(__file__).resolve().parent.parent / ".env.local"
    env_default = Path(__file__).resolve().parent.parent / ".env"

    if env_local.exists():
        load_dotenv(env_local)
    elif env_default.exists():
        load_dotenv(env_default)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("[%Y-%m-%d %H:%M:%S]")


def run_checks() -> dict:
    """Run all enabled checks and return results dict."""
    results = {}

    # App health checks
    results["apps"] = [check_app_health(name, url) for name, url in APPS]

    # Supabase
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if supabase_url and supabase_key:
        results["supabase"] = check_supabase(supabase_url, supabase_key)
    else:
        print(f"{_timestamp()} ⚠ Supabase check skipped — missing env vars")

    return results


def log_results(results: dict):
    """Print check results to stdout."""
    ts = _timestamp()
    print(f"{ts} Starting monitoring checks...")

    for app in results.get("apps", []):
        if app["status"] == "ok":
            print(f"{ts} ✓ {app['name']} — OK ({app['response_time_ms']}ms)")
        else:
            print(f"{ts} ✗ {app['name']} — DOWN ({app.get('error', 'unknown')})")

    if "supabase" in results:
        r = results["supabase"]
        if r["status"] == "ok":
            ms = r.get("response_time_ms", "?")
            print(f"{ts} ✓ Supabase — OK ({ms}ms)")
        else:
            print(f"{ts} ✗ Supabase — DOWN ({r.get('error', 'unknown')})")


def needs_alert(results: dict) -> bool:
    """Return True if any check warrants a Telegram alert."""
    for app in results.get("apps", []):
        if app["status"] != "ok":
            return True
    if "supabase" in results and results["supabase"]["status"] != "ok":
        return True
    return False


def send_alert(results: dict):
    """Format and send a Telegram alert if configured."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print(f"{_timestamp()} ⚠ Telegram not configured — skipping alert", file=sys.stderr)
        return

    message = format_alert_message(results)
    if not message:
        return

    print(f"{_timestamp()} Sending Telegram alert...")
    ok = send_telegram_alert(bot_token, chat_id, message)
    if ok:
        print(f"{_timestamp()} ✓ Alert sent")
    else:
        print(f"{_timestamp()} ✗ Alert failed", file=sys.stderr)


def test_alert():
    """Send a test message to verify Telegram configuration."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set", file=sys.stderr)
        sys.exit(1)

    message = "*SkatAI Monitor*\n_Test alert_ — Telegram is configured correctly."
    ok = send_telegram_alert(bot_token, chat_id, message)
    if ok:
        print("✓ Test alert sent successfully")
    else:
        print("✗ Test alert failed", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="SkatAI stack monitoring")
    parser.add_argument("--test-alert", action="store_true", help="Send a test Telegram message")
    args = parser.parse_args()

    _load_env()

    if args.test_alert:
        test_alert()
        return

    results = run_checks()
    log_results(results)

    if needs_alert(results):
        send_alert(results)

    # Exit 1 if any check failed
    any_failure = needs_alert(results)
    print(f"{_timestamp()} Done.")
    sys.exit(1 if any_failure else 0)


if __name__ == "__main__":
    main()

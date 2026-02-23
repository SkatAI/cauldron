"""Telegram alert sender."""

import sys
from datetime import datetime, timezone

import requests


def send_telegram_alert(bot_token: str, chat_id: str, message: str) -> bool:
    """Send a message via Telegram Bot API.

    Args:
        bot_token: Telegram bot token
        chat_id: Target chat/group ID
        message: Message text (Markdown)

    Returns:
        True on success, False on failure.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10,
        )
        if resp.status_code == 200:
            return True
        print(f"Telegram API error: {resp.status_code} {resp.text}", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"Telegram send failed: {exc}", file=sys.stderr)
        return False


def format_alert_message(results: dict) -> str:
    """Format check results into a Telegram-friendly Markdown message.

    Only includes sections with issues (non-ok status).
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [f"*SkatAI Monitor Alert*\n_{now}_\n"]

    for app in results.get("apps", []):
        if app["status"] != "ok":
            lines.append(f"*{app['name']}*: DOWN — {app.get('error', 'unknown')}")

    if "supabase" in results:
        r = results["supabase"]
        if r["status"] != "ok":
            lines.append(f"*Supabase*: DOWN — {r.get('error', 'unknown')}")

    if not lines[1:]:
        return ""

    return "\n".join(lines)

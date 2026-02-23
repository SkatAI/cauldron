# Monitoring Script Spec — SkatAI Stack

## Overview

Build a Python monitoring script that checks the health of all components of the SkatAI stack and sends alerts via Telegram when something is wrong or credits are running low.

Run as a cron job (locally or on Digital Ocean).

---

## Project Structure

```
monitor/
├── monitor.py          # main script
├── checks/
│   ├── __init__.py
│   ├── health.py       # HTTP health checks for DO apps
│   ├── supabase.py     # Supabase connectivity check
│   ├── openrouter.py   # OpenRouter credit check
│   └── langsmith.py    # LangSmith recent activity check
├── alerts/
│   ├── __init__.py
│   └── telegram.py     # Telegram alert sender
├── .env.example        # template for secrets
├── requirements.txt
└── README.md
```

---

## Environment Variables
see .env.local on local



---

## Module Specs

### `checks/health.py`

Function: `check_app_health(name: str, url: str, timeout: int) -> dict`

- HTTP GET to the app URL
- Returns `{"name": name, "url": url, "status": "ok"|"down", "http_code": int|None, "error": str|None, "response_time_ms": float}`
- Status is "ok" only if HTTP 200 received within timeout
- Catch all exceptions (ConnectionError, Timeout, etc.) and return status "down" with error message

Check all three apps: sociosim, cauldron, sociosim-adk-agent

### `checks/supabase.py`

Function: `check_supabase(url: str, anon_key: str, timeout: int) -> dict`

- HTTP GET to `{url}/rest/v1/` with header `apikey: {anon_key}`
- Returns `{"status": "ok"|"down", "error": str|None}`
- Status "ok" if HTTP 200

### `checks/openrouter.py`

Function: `check_openrouter_credits(api_key: str, threshold: float) -> dict`

- HTTP GET to `https://openrouter.ai/api/v1/credits`
- Header: `Authorization: Bearer {api_key}`
- Response JSON has field `data.total_credits` (total purchased) and `data.usage` (amount used)
- Remaining = total_credits - usage
- Returns `{"status": "ok"|"low"|"error", "remaining": float|None, "threshold": float, "error": str|None}`
- Status "low" if remaining < threshold

### `checks/langsmith.py`

Function: `check_langsmith(api_key: str, project_name: str) -> dict`

- HTTP GET to `https://api.smith.langchain.com/api/v1/runs`
- Query params: `project_name={project_name}&limit=1&start_time={24h_ago_iso}`
- Header: `x-api-key: {api_key}`
- Returns `{"status": "ok"|"inactive"|"error", "last_run_at": str|None, "error": str|None}`
- Status "inactive" if no runs in last 24h (not necessarily an alert, just informational)
- Status "error" if API call fails

### `alerts/telegram.py`

Function: `send_telegram_alert(bot_token: str, chat_id: str, message: str) -> bool`

- HTTP POST to `https://api.telegram.org/bot{bot_token}/sendMessage`
- Body: `{"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}`
- Returns True on success, False on failure
- Log failures to stderr but do not raise

Function: `format_alert_message(results: dict) -> str`

- Takes the full results dict from monitor.py
- Returns a nicely formatted Markdown message
- Only include sections with issues (don't spam with all-green status)
- Include timestamp

---

## `monitor.py` — Main Script

```
1. Load .env with python-dotenv
2. Run all checks (health x3, supabase, openrouter, langsmith)
3. Collect results into a single dict
4. Log all results to stdout with timestamp (always, for cron logs)
5. Determine if any alerts need to be sent:
   - Any app health check is "down"
   - Supabase is "down"
   - OpenRouter status is "low" or "error"
   - LangSmith status is "error" (inactive is just logged, not alerted)
6. If alerts needed: send Telegram message
7. Exit with code 0 (success) or 1 (if any check failed) — useful for cron monitoring
```

Also provide a CLI flag `--test-alert` that sends a test Telegram message and exits, so the user can verify Telegram is configured correctly.

---

## `requirements.txt`

```
requests>=2.31.0
python-dotenv>=1.0.0
```

No other dependencies. Keep it simple.

---

## Error Handling Philosophy

- **Never crash** — every check must catch all exceptions and return a structured error result
- Log everything to stdout/stderr for cron visibility
- A failure to send a Telegram alert should not crash the script

---

## Output Format (stdout)

```
[2024-01-15 10:30:00] Starting monitoring checks...
[2024-01-15 10:30:00] ✓ sociosim — OK (234ms)
[2024-01-15 10:30:01] ✗ cauldron — DOWN (Connection refused)
[2024-01-15 10:30:01] ✓ sociosim-adk-agent — OK (189ms)
[2024-01-15 10:30:02] ✓ Supabase — OK
[2024-01-15 10:30:02] ✓ OpenRouter — $7.43 remaining
[2024-01-15 10:30:03] ~ LangSmith — No runs in last 24h (informational)
[2024-01-15 10:30:03] 🚨 Sending Telegram alert...
[2024-01-15 10:30:03] Done.
```

---

## Notes for Claude Code

- Use only stdlib + requests + python-dotenv (no heavyweight frameworks)
- Python 3.10+ syntax is fine
- All checks should run sequentially (no async needed for this scale)
- Add a brief docstring to each function
- The `.env.example` file should have all keys with placeholder values and a comment explaining each one
- Write a short `README.md` with setup steps: clone, create .env, install requirements, test alert, add to cron

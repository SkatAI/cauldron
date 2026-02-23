# Deploying the Monitor as a Free Scheduled Job on Digital Ocean

## Overview

Digital Ocean App Platform supports **Jobs** — one-off or scheduled containers that run on a cron schedule. The free tier includes 3 free static sites, but for Jobs you need at least the **Basic** dyno ($0/month for jobs that run infrequently — you only pay for runtime, billed per second).

**Cost estimate:** A monitoring script that runs in ~5 seconds every 30 minutes = 240 runs/day × 5s = 1,200s/day. At ~$0.00001/second for the smallest instance, that's roughly **$0.01/day or ~$0.30/month**. Effectively free.

Alternatively, run it on **one of your existing DO apps** if they already run a server — add it as a background worker for zero extra cost.

---

## Option A — Add as a Job to an Existing DO App (Recommended, Zero Extra Cost)

If one of your existing apps (cauldron, sociosim) is already deployed on DO App Platform, you can add the monitor as a **scheduled job within that same app**.

### Steps

**1. Add the monitor code to one of your existing repos**

Copy the `monitor/` folder into the repo root of, say, `cauldron`.

```
cauldron/
├── monitor/
│   ├── monitor.py
│   ├── checks/
│   ├── alerts/
│   ├── requirements.txt
│   └── .env.example
├── ... (rest of cauldron)
```

**2. Edit the App Spec in the DO Console**

- Go to [cloud.digitalocean.com](https://cloud.digitalocean.com) → Apps → select your app (e.g. cauldron)
- Click **Settings** → **App Spec** → **Edit**

Add a `jobs:` section to the YAML:

```yaml
jobs:
  - name: monitor
    kind: PRE_DEPLOY        # use SCHEDULED for recurring
    run_command: pip install -r monitor/requirements.txt && python monitor/monitor.py
    instance_size_slug: basic-xxs
    instance_count: 1
```

For a **scheduled** job, use this instead:

```yaml
jobs:
  - name: monitor
    kind: SCHEDULED
    run_command: pip install -r monitor/requirements.txt && python monitor/monitor.py
    schedule: "*/30 * * * *"    # every 30 minutes (standard cron syntax)
    instance_size_slug: basic-xxs
    instance_count: 1
    envs:
      - key: SUPABASE_URL
        scope: RUN_TIME
        value: "your-value-here"
      - key: SUPABASE_ANON_KEY
        scope: RUN_TIME
        type: SECRET
        value: "your-secret-here"
      # ... add all other env vars
```

**3. Add Environment Variables**

In the DO Console: App → Settings → Environment Variables → Add each key from your `.env`.
Mark sensitive values (API keys, bot tokens) as **Encrypted**.

**4. Deploy**

Click **Save** — DO will redeploy and the scheduled job will start running automatically.

---


---

## Option C — Local Cron Job (Zero Cost, Requires Machine Always On)

If you have a machine (server, Raspberry Pi, or your laptop if always on):

```bash
# Install
cd /path/to/monitor
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values

# Test it works
python monitor.py --test-alert

# Add to crontab
crontab -e
```

Add this line:
```
*/30 * * * * cd /path/to/monitor && python monitor.py >> /var/log/monitor.log 2>&1
```

---

## Setting Up Telegram Alerts (5 minutes)

Telegram has a free, simple bot API — perfect for alerts.

### Step 1 — Create a Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g. "SkatAI Monitor") and a username (e.g. `skatai_monitor_bot`)
4. BotFather replies with your **bot token** — save it: `123456789:ABCdef...`

### Step 2 — Get Your Chat ID

1. Search for your new bot in Telegram and click **Start**
2. Send it any message (e.g. "hello")
3. Visit this URL in your browser (replace `YOUR_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
4. In the JSON response, find `result[0].message.chat.id` — that's your **chat ID** (a number like `987654321`)

### Step 3 — Test It

Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in your `.env`, then:

```bash
python monitor.py --test-alert
```

You should receive a test message on Telegram instantly.

### Step 4 — Add to `.env`

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=987654321
```

---

## Cron Schedule Reference

| Schedule | Cron expression |
|----------|----------------|
| Every 30 min | `*/30 * * * *` |
| Every hour | `0 * * * *` |
| Every 15 min | `*/15 * * * *` |
| Daily at 8am | `0 8 * * *` |

---

## Checking Job Logs on DO

- DO Console → Apps → your app → **Activity** tab → click any job run to see logs
- Logs show stdout/stderr from the script, including all check results

---

## Recommended Approach for You

Given you already have 3 apps on DO, add the monitor as a **scheduled job inside the cauldron app** (Option A). It costs nothing extra, shares the same environment, and you can manage all env vars in one place.

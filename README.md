# Rising Claw Bot

Headless daily claw automation using Playwright. Runs on macOS, Linux VPS, and Raspberry Pi without installing system browsers manually. Supports multiple accounts in a single run.

## Requirements

- Python 3.11+
- Network access to your configured site

## Setup

```bash
git clone <repo-url>
cd Risinghub-claw-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
cp accounts.example.json data/accounts.json
```

Edit `.env` (app-wide settings only):

```env
BASE_URL=https://example.test
HEADLESS=true
```

Edit `data/accounts.json` with your account credentials (see [Accounts](#accounts) below).

## Accounts

Copy `accounts.example.json` to `data/accounts.json` and replace placeholders. Each entry is one site login the bot runs sequentially on every invocation.

### Schema

```json
[
  {
    "id": "main",
    "username": "test_user_01",
    "password": "CHANGE_ME",
    "heroes": ["HeroOne", "HeroTwo"]
  },
  {
    "id": "alt",
    "username": "test_user_02",
    "password": "CHANGE_ME"
  }
]
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | Short unique label (used in logs, Discord, and data paths) |
| `username` | yes | Site login username |
| `password` | yes | Site login password |
| `heroes` | no | Ordered list of hero names for rotation (see below) |

`id` values must be unique. If `heroes` is omitted, the bot scrapes the hero list on first run and saves it to that account's `heroes.json`.

### Hero rotation

Each account gets **one claw claim per run** (the site allows one daily claim per login). The optional `heroes` list controls **which hero is picked on which day**, not how many claims happen in a single run.

When `heroes` is set, the bot reads that account's prize log and picks the next hero in the list (wrapping back to the first after the last). When omitted, heroes are scraped once and stored in `data/accounts/{id}/heroes.json`; rotation then uses that saved list.

## Run manually

```bash
python -m risingclaw.main
```

One invocation processes every account in `data/accounts.json` in order. Accounts that already ran today are skipped; a failure on one account does not stop the others.

If the claw is still on cooldown for an account (site timer not cleared), the bot logs the message and continues — no Discord alert, that account is not counted as a failure, and the process exit code stays 0 unless another account failed.

Optional `DISCORD_WEBHOOK` sends a formatted embed on success (account, hero, prize, quantity) and `@everyone` alerts on failures. Success embeds include an **Account** field with the account `id`. Error messages are prefixed with `[account_id]`. Cooldown skips are not sent to Discord.

## Data files

Global:

| Path | Purpose |
|------|---------|
| `data/accounts.json` | Account credentials and optional hero lists |

Per account (`{id}` = the account's `id` field):

| Path | Purpose |
|------|---------|
| `data/accounts/{id}/log.json` | Prize history for that account |
| `data/accounts/{id}/cookies.json` | Saved session (Playwright storage state) |
| `data/accounts/{id}/heroes.json` | Scraped hero list when `heroes` is not set in accounts.json |
| `data/accounts/{id}/debug/` | Screenshots and HTML on failures |

**Note:** Old Selenium `cookie.pkl` and Excel `log.xlsx` files are not migrated. Expect one fresh login and a new JSON log on first run after upgrading.

## Migrating from single-account

If you previously used `USERNAME`, `PASSWORD`, and `HEROES` in `.env` with files under `data/`:

1. Create `data/accounts.json` with at least one entry. Use `"id": "main"` (or any short label) and move credentials from `.env` into that entry.
2. If you had `HEROES=HeroOne,HeroTwo` in `.env`, add `"heroes": ["HeroOne", "HeroTwo"]` to the account entry.
3. Move existing data files into the per-account folder (replace `main` with your account `id`):
   - `data/cookies.json` → `data/accounts/main/cookies.json`
   - `data/log.json` → `data/accounts/main/log.json`
   - `data/heroes.json` → `data/accounts/main/heroes.json`
4. Remove `USERNAME`, `PASSWORD`, and `HEROES` from `.env`.

The bot does not read credentials from `.env` anymore. If `data/accounts.json` is missing or empty, startup fails during setup checks (`SetupChecks`) with a message to copy `accounts.example.json`. The loader warns and returns an empty list when the file is absent, but setup validates accounts and raises before the run loop starts.

## Daily run guard

The bot skips an account if it already logged a prize after **01:00 Europe/Amsterdam** on the current calendar day (before 01:00, "today" means since yesterday 01:00). The check is per account.

## Scheduling on a VPS

Set `TZ=Europe/Amsterdam` in the environment so logs and cooldown logic align with local expectations.

No deploy changes are needed for multiple accounts — the same cron job or systemd timer runs `python -m risingclaw.main` once, and the bot processes all configured accounts sequentially.

### Cron

See [`deploy/cron.example`](deploy/cron.example). Example:

```cron
5 2 * * * TZ=Europe/Amsterdam cd /path/to/Risinghub-claw-bot && /path/to/venv/bin/python -m risingclaw.main >> /path/to/Risinghub-claw-bot/cron.log 2>&1
```

### systemd

Copy and edit paths in [`deploy/risingclaw.service`](deploy/risingclaw.service) and [`deploy/risingclaw.timer`](deploy/risingclaw.timer), then:

```bash
sudo cp deploy/risingclaw.service deploy/risingclaw.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now risingclaw.timer
```

Check status:

```bash
systemctl list-timers risingclaw.timer
journalctl -u risingclaw.service
```

## Troubleshooting

- **Browser missing:** run `playwright install chromium` inside the same venv.
- **Login fails:** check `data/accounts/{id}/debug/` for screenshots and page HTML.
- **Selectors broken:** the target site may have changed; update locators in `risingclaw/operations/claw.py` and related modules.
- **accounts.json missing or invalid:** startup fails during setup checks before any account runs (not silently at load time). Copy `accounts.example.json` to `data/accounts.json` and fill in at least one account. Invalid JSON, empty arrays, or duplicate `id` values also fail at setup.

## Smoke test checklist

1. Fresh run with no cookies → login → claw → JSON log entry per account
2. Second run same day → each account exits early with "already ran today"
3. Run with saved cookies → skips login per account
4. Induce a failure on one account → other accounts still run; screenshot + HTML in that account's `debug/`
5. Discord success embed shows account id, hero, prize, and quantity
6. Same venv + `playwright install chromium` on Mac and VPS

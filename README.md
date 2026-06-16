# Rising Claw Bot

Headless daily claw automation using Playwright. Runs on macOS, Linux VPS, and Raspberry Pi without installing system browsers manually.

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
```

Edit `.env`:

```env
BASE_URL=https://example.test
USERNAME=your_username
PASSWORD=your_password
HEROES=HeroOne,HeroTwo
HEADLESS=true
```

`HEROES` is optional. If omitted, the bot scrapes the hero list on first run and saves it to `data/heroes.json`.

## Run manually

```bash
python -m risingclaw.main
```

## Data files

| Path | Purpose |
|------|---------|
| `data/log.json` | Prize history |
| `data/cookies.json` | Saved session (Playwright storage state) |
| `data/heroes.json` | Scraped hero list when `HEROES` is not set |
| `data/debug/` | Screenshots and HTML on failures |

**Note:** Old Selenium `cookie.pkl` and Excel `log.xlsx` files are not migrated. Expect one fresh login and a new JSON log on first run after upgrading.

## Daily run guard

The bot skips execution if it already logged a prize after **01:00 Europe/Amsterdam** on the current calendar day (before 01:00, "today" means since yesterday 01:00).

## Scheduling on a VPS

Set `TZ=Europe/Amsterdam` in the environment so logs and cooldown logic align with local expectations.

### Cron

See [`deploy/cron.example`](deploy/cron.example). Example:

```cron
5 1 * * * TZ=Europe/Amsterdam cd /path/to/Risinghub-claw-bot && /path/to/venv/bin/python -m risingclaw.main >> /path/to/Risinghub-claw-bot/cron.log 2>&1
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
- **Login fails:** check `data/debug/` for screenshots and page HTML.
- **Selectors broken:** the target site may have changed; update locators in `risingclaw/operations/claw.py` and related modules.

## Smoke test checklist

1. Fresh run with no cookies → login → claw → JSON log entry
2. Second run same day → exits early with "already ran today"
3. Run with saved cookies → skips login
4. Induce a failure → screenshot + HTML in `data/debug/`
5. Same venv + `playwright install chromium` on Mac and VPS

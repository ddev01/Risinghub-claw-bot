---
name: multi-account-bootstrap
description: Refactors main.py, SetupChecks, DiscordNotifier, and BrowserSession bootstrap for single config load in the multi-account claw bot. Use after config/storage agents complete; wires orchestration and notification APIs.
---

You are a staff engineer refactoring the bootstrap/orchestration layer of Risinghub-claw-bot.

## Prerequisites

Run AFTER `multi-account-config` and `multi-account-storage` agents finish. Assume:
- `has_already_run(account, timezone: str)` exists
- `PrizeLog` no longer writes `"account"` field
- `save_failure_artifacts(page, label, account)` requires `account`

## Scope (file ownership)

- `risingclaw/main.py`
- `risingclaw/checks/setup_checks.py`
- `risingclaw/services/discord_notifier.py`
- `risingclaw/services/browser_setup.py` (Phase A only: remove unused `account` param)

## Objectives

1. **Single config load**
   - `SetupChecks.__init__(self, config: AppConfig)` — inject config, no internal `load_config()`
   - `SetupChecks.run() -> list[AccountConfig]` — return validated accounts
   - `main.py`:
     ```python
     app_config = load_config()
     notifier = DiscordNotifier.from_config(app_config)
     accounts = SetupChecks(app_config).run()
     for account in accounts:
         if has_already_run(account, app_config.timezone): ...
         result = ClawRunner(app_config, account).run()
         notifier.notify_success(result)
     ```
   - Remove second `load_accounts()` call from `main`

2. **Discord API cleanup** (`discord_notifier.py`)
   - Remove `Config = AppConfig` alias usage — import `AppConfig` directly
   - `notify_success(result: PrizeResult)` — use `result.account_id` only, drop `account_id` param
   - Update `main.py` call site

3. **BrowserSession cleanup** (`browser_setup.py`)
   - Remove unused `account: AccountConfig | None` parameter from `__init__`
   - Update `ClawRunner` caller only (minimal change to pass one fewer arg)
   - Do NOT implement `storage_state` on start — that is the runner agent (Phase C)

4. **Pass config through**
   - Ensure `DiscordNotifier.from_config(app_config)` receives config from main
   - `ClawRunner` already receives `app_config` — verify no silent `load_config()` re-loads in hot path

## Constraints

- Preserve: sequential account loop, skip-if-ran, failure aggregation, cooldown non-fatal, Discord embed fields
- Do NOT commit changes
- Do NOT implement cookie session simplification (runner agent owns Phase C)

## When done

Report: files changed, confirm import smoke test passes:
`python -c "from risingclaw.config import load_config; from risingclaw.checks.setup_checks import SetupChecks; SetupChecks(load_config()).run()"`

---
name: multi-account-config
description: Refactors AppConfig, AccountConfig, account_store, errors, and already_ran for the multi-account claw bot. Use proactively during multi-account refactors for config-layer dead code removal and timezone wiring.
---

You are a staff engineer refactoring the config layer of Risinghub-claw-bot.

## Scope (file ownership — do not touch files outside this list)

- `risingclaw/config.py`
- `risingclaw/account.py`
- `risingclaw/errors.py`
- `risingclaw/managers/account_store.py`
- `risingclaw/checks/already_ran.py`

## Objectives

1. **Remove dead config surface**
   - Delete `AlreadyRanError` from `errors.py` (never raised)
   - Delete unused `AppConfig.login_url`, `claw_url`, `profile_url` properties
   - Keep `AppConfig.timezone` — it will be wired into daily guard

2. **Simplify account_store**
   - Replace `_accounts_path(app_config)` getattr fallback with direct `app_config.accounts_path`

3. **Wire timezone into daily guard**
   - Change `has_already_run(account)` → `has_already_run(account, timezone: str)`
   - Replace hardcoded `"Europe/Amsterdam"` with `pytz.timezone(timezone)`
   - Do NOT update `main.py` call sites — the bootstrap agent owns that

4. **Account URL helpers**
   - Keep URL properties on `AccountConfig` only (single source of truth)
   - Optional: extract a tiny shared URL helper in `account.py` if it reduces duplication without adding a new module

## Constraints

- Preserve user-facing behavior: daily skip after 01:00 in configured timezone
- Do NOT commit changes
- Privacy: no production URLs, hosts, or credentials in code
- Minimal diff — delete dead code, don't redesign unrelated pieces
- Leave repo importable: `python -c "from risingclaw.config import load_config; from risingclaw.checks.already_ran import has_already_run"`

## When done

Report: files changed, signature changes (especially `has_already_run`), anything the bootstrap agent must wire up.

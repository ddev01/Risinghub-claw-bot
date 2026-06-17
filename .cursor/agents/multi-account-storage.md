---
name: multi-account-storage
description: Refactors per-account storage (PrizeLog, debug artifacts, authentication) for the multi-account claw bot. Use proactively during multi-account refactors for log simplification and I/O cleanup.
---

You are a staff engineer refactoring per-account storage and auth cleanup in Risinghub-claw-bot.

## Scope (file ownership — do not touch files outside this list)

- `risingclaw/managers/prize_log.py`
- `risingclaw/utilities/debug_artifacts.py`
- `risingclaw/services/authentication.py`

## Objectives

1. **Simplify PrizeLog** (`prize_log.py`)
   - Drop `"account"` key from new log entries (each account has its own file)
   - Remove `_entries_for_account` — `read_last()` returns last entry from `_read_all()` directly
   - Existing log files with `"account"` field must remain readable

2. **Tighten debug artifacts** (`debug_artifacts.py`)
   - Make `account: AccountConfig` a required parameter (all 7 call sites already pass it)
   - Remove `load_config` import and global debug-dir fallback

3. **Remove dead auth code** (`authentication.py`)
   - Delete `accept_consent` method and the commented-out call in `login()`

## Constraints

- Preserve user-facing behavior: hero rotation still reads last log entry correctly
- Do NOT commit changes
- Do NOT touch `main.py`, `claw.py`, or Discord code
- Minimal diff — no new manager classes for heroes

## When done

Report: files changed, any caller assumptions broken (there should be none outside your scope).

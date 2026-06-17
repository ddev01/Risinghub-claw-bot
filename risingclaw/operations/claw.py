import json
import re
from os.path import exists

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from ..account import AccountConfig
from ..errors import BrowserError, ClawCooldownError, ClawError
from ..managers.prize_log import PrizeLog
from ..prize_result import PrizeResult
from ..services.hide_stuff import hide_stuff
from ..utilities.debug_artifacts import save_failure_artifacts
from ..utilities.logger import time_print


class Claw:
    def __init__(self, page: Page, prize_log: PrizeLog, account: AccountConfig):
        self.page = page
        self.prize_log = prize_log
        self.account = account

    def claim_prize(self, hero: str) -> PrizeResult:
        time_print(f"Claiming prize for {hero}")
        hide_stuff(self.page)
        try:
            self._wait_for_claw_ready()
            timeout = self._read_cooldown()
            time_print(f"Cooldown timer: {timeout!r}")

            if not self._cooldown_is_clear(timeout):
                raise ClawCooldownError(
                    f"Claw on cooldown ({timeout}). No prize claimed."
                )

            time_print("No cooldown. Proceeding to claim prize.")
            self.page.locator("#speedclaw").click(timeout=10_000)
            self.page.wait_for_timeout(500)

            self.page.locator(".hero-claw").filter(
                has=self.page.locator(".hero-content div", has_text=hero)
            ).first.click(timeout=10_000)
            self.page.locator("#button div").filter(has_text="ok").wait_for(
                state="attached",
                timeout=10_000,
            )
            time_print("Hero selected, clicking start.")
            self.page.locator("#button").click(timeout=10_000)

            self._wait_for_prize_result()
            prize_name_text = self._read_element_text("#prize-name")
            prize_info_text = self._read_element_text("#prize-info")

            time_print(f"Prize name: {prize_name_text}")
            time_print(f"Prize info: {prize_info_text}")
            self.prize_log.append(hero, prize_name_text, prize_info_text)
            return PrizeResult(
                account_id=self.account.id,
                hero=hero,
                prize=prize_name_text,
                quantity=prize_info_text,
            )
        except ClawError:
            raise
        except PlaywrightTimeoutError as exc:
            save_failure_artifacts(self.page, "claim-prize-timeout", self.account)
            raise BrowserError(f"Error during prize claim process: {exc}") from exc
        except Exception as exc:
            save_failure_artifacts(self.page, "claim-prize-error", self.account)
            raise BrowserError(f"Error checking cooldown or claiming prize: {exc}") from exc

    def _wait_for_claw_ready(self) -> None:
        self.page.locator("#claw-container").wait_for(state="attached", timeout=10_000)
        self.page.locator("#speedclaw").wait_for(state="visible", timeout=10_000)
        self.page.wait_for_function("() => typeof jQuery !== 'undefined'", timeout=10_000)

    def _read_cooldown(self) -> str:
        self.page.locator("#countdown-container h3").wait_for(state="attached", timeout=10_000)
        for _ in range(10):
            text = self._read_element_text("#countdown-container h3")
            if re.search(r"\d+\s*:\s*\d+\s*:\s*\d+", text):
                return text
            self.page.wait_for_timeout(500)

        countdown_visible = self.page.evaluate(
            """
            () => {
                const container = document.querySelector('#countdown-container');
                return container && container.style.visibility === 'visible';
            }
            """
        )
        if not countdown_visible:
            return "00 : 00 : 00"
        raise BrowserError("Countdown timer did not load.")

    def _cooldown_is_clear(self, timeout: str) -> bool:
        parts = [part.strip() for part in timeout.split(":")]
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise BrowserError(f"Unexpected countdown format: {timeout!r}")
        return all(part == "00" for part in parts)

    def _wait_for_prize_result(self) -> None:
        self.page.wait_for_function(
            """
            () => {
                const container = document.querySelector('#prize-container');
                const prizeName = document.querySelector('#prize-name');
                if (!container || !prizeName) {
                    return false;
                }
                const name = prizeName.textContent.trim();
                return container.style.visibility === 'visible'
                    && name.length > 0
                    && name !== 'Name';
            }
            """,
            timeout=30_000,
        )

    def _read_element_text(self, selector: str) -> str:
        return self.page.evaluate(
            """
            (selector) => document.querySelector(selector)?.textContent.trim() ?? ''
            """,
            selector,
        )

    def pick_hero(self) -> str:
        self.page.goto(self.account.claw_url)
        self._wait_for_claw_ready()
        time_print("Picking hero")

        heroes = self._heroes_from_account()
        if heroes:
            time_print(f"Heroes for account: {heroes}")
            last_entry = self.prize_log.read_last()
            if last_entry:
                time_print(
                    "Last entry: "
                    f"{last_entry['date']} {last_entry['time']} "
                    f"{last_entry['hero']} {last_entry['prize']}"
                )
                if last_entry["hero"] in heroes:
                    current_index = heroes.index(last_entry["hero"])
                    next_index = (current_index + 1) % len(heroes)
                    return heroes[next_index]
                time_print(
                    "Last entry hero was not found in configured heroes. "
                    "User probably removed the hero from the account config."
                )
                return heroes[0]
            time_print("Prize log is empty. This is the first run.")
            return heroes[0]

        time_print("No heroes configured for account")
        time_print("Fetching heroes from the claw.")
        self.page.locator("#heroes-container").wait_for(timeout=10_000)
        options = self.page.locator(
            ".hero-claw .hero-content div:first-child"
        ).all_inner_texts()
        options = [hero.strip() for hero in options if hero.strip()]
        if not options:
            save_failure_artifacts(self.page, "no-heroes-found", self.account)
            raise BrowserError("No heroes found on the claw page.")
        time_print(f"Fetched heroes: {options}")
        self.save_heroes(options)
        return options[0]

    def _heroes_from_account(self) -> list[str] | None:
        if self.account.heroes:
            return [hero.strip() for hero in self.account.heroes if hero.strip()]
        if exists(self.account.heroes_path):
            with open(self.account.heroes_path, encoding="utf-8") as file:
                data = json.load(file)
            heroes = data.get("heroes", [])
            return [hero.strip() for hero in heroes if hero.strip()]
        return None

    def save_heroes(self, heroes: list[str]) -> None:
        time_print("Saving heroes list")
        with open(self.account.heroes_path, "w", encoding="utf-8") as file:
            json.dump({"heroes": heroes}, file, indent=2)

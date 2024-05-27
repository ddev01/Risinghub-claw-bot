from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from os import getenv, environ
from ..utilities.logger import time_print
from ..managers.excel_manager import ExcelManager


class Claw:
    def __init__(self, driver, excel_manager):
        self.driver = driver
        self.excel_manager = excel_manager

    def claim_prize(self, hero):
        time_print(f"Claiming prize for {hero}")
        # Hide any garbage that can possible block the buttons.
        hide_script = """
        var ads = document.querySelectorAll('.adsbygoogle');
        ads.forEach(function(el) { el.style.display = 'none'; });
        var iframes = document.querySelectorAll('iframe');
        iframes.forEach(function(el) { el.style.display = 'none'; });
        """
        self.driver.execute_script(hide_script)
        try:
            timeout_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="countdown-container"]/h3')
                )
            )
            # Execute JavaScript to get the text content directly
            timeout = self.driver.execute_script(
                "return arguments[0].textContent.trim();", timeout_element
            )
            if timeout == "00 : 00 : 00":
                time_print("No cooldown. Proceeding to claim prize.")
                try:
                    # Code to execute when there is no cooldown
                    speed_claw_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="speedclaw"]'))
                    )
                    speed_claw_button.click()

                    hero_card_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[contains(text(), "' + hero + '")]')
                        )
                    )
                    hero_card_button.click()

                    ok_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//div[@id='button' and @onclick='start();']")
                        )
                    )
                    ok_button.click()

                    time_print("Clicked the 'ok' button.")

                    # Wait for the prize name element to be present and retrieve its text
                    prize_name_element = WebDriverWait(self.driver, 10).until(
                        lambda driver: (
                            driver.find_element(By.ID, "prize-name")
                            if driver.find_element(By.ID, "prize-name").text != "Name"
                            else False
                        )
                    )
                    prize_name_text = prize_name_element.text

                    # Correctly wait for the prize info element to have text other than "Info"
                    prize_info_element = WebDriverWait(self.driver, 10).until(
                        lambda driver: (
                            driver.find_element(By.ID, "prize-info")
                            if driver.find_element(By.ID, "prize-info").text != "Info"
                            else False
                        )
                    )
                    prize_info_text = prize_info_element.text

                    time_print(f"Prize name: {prize_name_text}")
                    time_print(f"Prize info: {prize_info_text}")
                    self.excel_manager.log_to_excel(
                        hero, prize_name_text, prize_info_text
                    )
                except Exception as e:
                    time_print(f"Error during prize claim process. Message: {e}")
            else:
                time_print(f"Prize already claimed today. Cooldown active. {timeout}")
                return
        except Exception as e:
            time_print(f"Error checking cooldown or claiming prize. Message: {e}")

    def pick_hero(self):
        self.driver.get("https://risinghub.net/claw")
        time_print("Picking heroe")
        heroes = getenv("HEROES")
        if heroes:
            heroes = heroes.split(",")
            time_print(f"Heroes in .env: {heroes}")
            last_entry = self.excel_manager.read_last_prize()
            if last_entry:
                time_print(
                    f"Last entry: {last_entry['date']} {last_entry['time']} {last_entry['hero']} {last_entry['prize']}"
                )
                if last_entry["hero"] in heroes:
                    current_index = heroes.index(last_entry["hero"])
                    next_index = (current_index + 1) % len(heroes)
                    return heroes[next_index]
                else:
                    time_print(
                        "Last entry hero was not found in env heroes. User probably removed the hero from the env file."
                    )
                    return heroes[0]
            else:
                time_print("Excel only contains headers. This is the first run.")
                return heroes[0]
        else:
            time_print("No heroes found in .env file")
            time_print("Fetching heroes from the claw.")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "heroes-container"))
            )
            heroes_container = self.driver.find_element(By.ID, "heroes-container")
            hero_elements = heroes_container.find_elements(
                By.CSS_SELECTOR, ".hero-claw .hero-content div:first-child"
            )
            options = [hero.text for hero in hero_elements]
            print("Fetched heroes:", options)
            self.update_env_file(options)
            return options[0]

    def update_env_file(self, heroes):
        time_print("Updating .env file with new heroes")
        with open(".env", "a") as env_file:
            heroes_value = ",".join(heroes)
            env_file.write(f"\nHEROES={heroes_value}")
        environ["HEROES"] = (
            heroes_value  # Update the environment variable for the current session
        )

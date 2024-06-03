from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement  # Import WebElement

def await_element_text_change(driver: WebDriver, by_type: By, element_identifier: str, unwanted_texts: list[str], timeout: int = 10) -> WebElement | None:
    """
    Wait for an element that does not contain any of the specified unwanted texts.

    :param driver: The WebDriver instance.
    :param by_type: The type of the locator (e.g., By.ID, By.CLASS_NAME).
    :param element_identifier: The identifier for the element (e.g., "prize-name").
    :param unwanted_texts: List of texts that should not be present in the element.
    :param timeout: Maximum time to wait for the element.
    :return: The WebElement if found, None otherwise.
    """
    return WebDriverWait(driver, timeout).until(
        lambda d: (
            element := d.find_element(by_type, element_identifier),
            element.text not in unwanted_texts and element.text.strip() != ""
        )[0]
    )
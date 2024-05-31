from selenium.webdriver.remote.webdriver import WebDriver

def hide_stuff(driver: WebDriver):
    hide_script = """
    var ads = document.querySelectorAll('.adsbygoogle');
    ads.forEach(function(el) { el.style.display = 'none'; });
    var iframes = document.querySelectorAll('iframe');
    iframes.forEach(function(el) { el.style.display = 'none'; });
    """
    driver.execute_script(hide_script)
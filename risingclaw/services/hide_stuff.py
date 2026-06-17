from playwright.sync_api import Page


def hide_stuff(page: Page) -> None:
    page.evaluate(
        """
        () => {
            document.querySelectorAll('.adsbygoogle').forEach((el) => {
                el.style.display = 'none';
            });
            document.querySelectorAll('iframe').forEach((el) => {
                el.style.display = 'none';
            });
        }
        """
    )

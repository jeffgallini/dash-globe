from selenium.webdriver import ChromeOptions


def pytest_setup_options():
    """Provide CI-stable Chrome options for dash[testing] browser fixtures."""
    options = ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-webgl")
    options.add_argument("--ignore-gpu-blocklist")
    options.add_argument("--no-sandbox")
    options.add_argument("--use-angle=swiftshader")
    options.add_argument("--use-gl=angle")
    options.add_argument("--window-size=1920,1080")
    return options

import atexit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

options = Options()

capabilities = DesiredCapabilities.CHROME.copy()
capabilities["platform"] = "WINDOWS"

hub_url = 'http://localhost:4444/wd/hub'

driver = webdriver.Remote(
  command_executor=hub_url,
  options=options,
  desired_capabilities=capabilities
)

while True:
    if driver.window_handles:
        # the browser window is still open
        continue
    else:
        # the browser window has been closed
        break   

driver.quit()
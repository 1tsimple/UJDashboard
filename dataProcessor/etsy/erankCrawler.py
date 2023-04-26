import time
import threading
from typing import Self

from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchWindowException

class CrawlerManager:
  __slots__ = "options", "drivers"
  
  _instance = None # Singleton Instance
  _lock = threading.Lock() # Thread Safety
  def __new__(cls) -> Self: # Singleton Constructor
    if cls._instance is None:
      with cls._lock:
        if not cls._instance:
          cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self) -> None:
    self.options = Options()
    self.drivers = []
    self.__init()
  
  def __init(self) -> None:
    self.options.add_argument('--disable-web-security')
    self.options.add_argument('--ignore-certificate-errors')
    self.options.add_argument('--disable-dev-shm-usage')
    self.options.add_argument('--disable-extensions')
    self.options.add_argument('--disable-gpu')
    self.options.add_argument('--no-sandbox')
    self.options.add_argument('--disable-infobars')
    self.options.add_experimental_option("detach", True)
  
  def get_driver(self) -> webdriver.Remote:
    driver = Remote(
      command_executor=f"http://localhost:4444/wd/hub",
      options=self.options,
    )
    self.add_driver(driver)
    return driver
  
  def add_driver(self, driver: webdriver.Remote) -> None:
    self.drivers.append(driver)
  
  def remove_driver(self, driver: webdriver.Remote) -> None:
    self.drivers.remove(driver)
  
  def check_crawlers(self) -> None:
    while True:
      for driver in self.drivers:
        if self.is_webdriver_closed(driver):
          driver.quit()
          self.remove_driver(driver)
      time.sleep(3)
  
  @staticmethod
  def is_webdriver_closed(driver) -> bool:
    try:
        return driver.execute_script("return document.readyState") != "complete"
    except NoSuchWindowException:
        return True
  
  def start(self) -> None:
    thread = threading.Thread(target=self.check_crawlers, daemon=True)
    thread.start()
  
  @staticmethod
  def get_page_source(driver: webdriver.Remote) -> str:
    source = driver.page_source
    css = driver.execute_script("""
      var css = [];
      for (var i=0; i<document.styleSheets.length; i++) {
        var cssText = '';
        var sheet = document.styleSheets[i];
        try {
          if (sheet.cssRules || sheet.rules) {
            var rules = sheet.cssRules || sheet.rules;
            for (var j=0; j<rules.length; j++) {
              cssText += rules[j].cssText;
            }
          }
        } catch (e) {
          console.warn('Could not retrieve CSS from ' + sheet.href, e);
        }
        css.push(cssText);
      }
      return css.join('\\n');
    """)
    return source + "\n<style>" + css + "</style>"
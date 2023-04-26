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
import threading
from typing import Self

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class CrawlerManager:
  __slots__ = "service", "options", "driver"
  
  _instance = None # Singleton Instance
  _lock = threading.Lock() # Thread Safety
  def __new__(cls) -> Self: # Singleton Constructor
    if cls._instance is None:
      with cls._lock:
        if not cls._instance:
          cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self) -> None:
    self.service = Service(ChromeDriverManager().install())
    self.options = Options()
    self.driver = None
    self.__init()
  
  def __init(self) -> None:
    self.options.add_experimental_option("detach", True)
  
  def init_crawler(self) -> None:
    self.driver = webdriver.Chrome(
      service=self.service,
      options=self.options
    )
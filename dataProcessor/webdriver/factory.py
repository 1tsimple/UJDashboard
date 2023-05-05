import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import logging
import asyncio
import threading
import pyperclip
import io
import csv

from typing import Self, Literal
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

DEFAULT_DRIVER_OPTIONS = [
  "--disable-web-security",
  "--ignore-certificate-errors",
  "--disable-dev-shm-usage",
  "--disable-extensions",
  "--disable-gpu",
  "--no-sandbox",
  "--disable-infobars"
]

class DriverNotInitialized(Exception): ...

class WebdriverController(ABC):
  __slots__ = "_hub_url", "options", "driver", "session_id", "wait", "action"
  
  def __init__(self, hub_url: str) -> None:
    self._hub_url = hub_url
    self.options = Options()
    self.set_options()
    self.driver = Remote(
      command_executor=self._hub_url,
      options=self.options,
    )
    self.session_id: str = self.driver.session_id # type: ignore
    self.wait = WebDriverWait(self.driver, 5)
    self.action = ActionChains(self.driver)
  
  def set_options(self): ...
  
  @abstractmethod
  def initialize(self): ...
  
  @property
  def is_closed(self) -> bool:
    try:
      return self.driver.execute_script("return document.readyState") != "complete"
    except NoSuchWindowException:
      return True
  
  def get_page_source(self) -> str:
    source = self.driver.page_source
    css = self.driver.execute_script(
      """
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
      """
    )
    return source + "\n<style>" + css + "</style>"
  
  def search_keyword_data(self, keyword: str): ...
  
  def get_keyword_data(self) -> dict[str, list[list[str]]]: ...

class ErankKeywordScrapper(WebdriverController):
  __slots__ = tuple()
  
  URL = "https://erank.com/"
  
  def __init__(self, hub_url: str) -> None:
    super().__init__(hub_url)
    logging.info("ErankKeywordScrapper object with Session ID '{session_id}' has been created and initialized. {debug_info}".format(session_id=self.session_id, debug_info={"ObjectID": id(self)}))
  
  def set_options(self):
    global DEFAULT_DRIVER_OPTIONS
    for option in DEFAULT_DRIVER_OPTIONS:
      self.options.add_argument(option)
    self.options.add_argument("start-maximized")
    self.options.add_experimental_option("prefs", {"download.default_directory": os.path.abspath(os.path.join(SCRIPT_DIR, "storage/erank"))})
  
  def initialize(self) -> None:
    self.driver.get(self.URL)
    self._log_in()
    self._open_new_tab()
  
  def _log_in(self) -> None:
    log_in_link = self.wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "Login")))
    log_in_link.click()
    
    email_input = self.wait.until(EC.visibility_of_element_located((By.ID, "signin-email")))
    email_input.send_keys(os.environ.get("erank_email"))
    
    password_input = self.wait.until(EC.visibility_of_element_located((By.ID, "signin-password")))
    password_input.send_keys(os.environ.get("erank_password"))
    
    log_in_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(),'Login')]")))
    log_in_button.click()
  
  def _open_new_tab(self) -> None:
    self.driver.execute_script("window.open('');")
    self.driver.switch_to.window(self.driver.window_handles[-1])
    self.driver.get(self.URL)
  
  def search_keyword_data(self, keyword: str) -> None:
    self.driver.get(f'{self.URL}keyword-tool?keywords={keyword.replace(" ", "+")}&country=USA')
    self.driver.switch_to.window(self.driver.window_handles[0])
    self.driver.get(f'{self.URL}keyword-explorer?keywords={keyword.replace(" ", "+")}&country=USA&source=etsy')
    self.driver.switch_to.window(self.driver.window_handles[-1])
  
  def get_keyword_data(self) -> dict[str, list[list[str]]]:
    keyword_tool_data_raw = self.__get_page_data()
    self.driver.switch_to.window(self.driver.window_handles[0])
    keyword_research_data_raw = self.__get_page_data()
    
    keyword_tool_data = list(map(lambda list_: list_[0:-1], keyword_tool_data_raw))
    keyword_research_data = list(map(self.__clean_erank_search_data, keyword_research_data_raw))
    return {"keyword-tool-data": keyword_tool_data, "keyword-research-data": keyword_research_data}
  
  def __get_page_data(self):
    export_button = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.kt-custom-dlbtn")))
    export_button.click()
    export_button.find_element(By.CSS_SELECTOR, ".dt-button.buttons-copy").click()
    text = pyperclip.paste()
    data = csv.reader(io.StringIO(text), delimiter="\t")
    for _ in range(3):
      next(data)
    return data
  
  @staticmethod
  def __clean_erank_search_data(__list: list[str]) -> list[str]:
    keyword = __list.pop(0).lstrip("\xa0 ")
    __list.insert(0, keyword)
    return __list

class WebdriverControllerFactory:
  factories = {
    "ErankKeywordScrapper": ErankKeywordScrapper
  }
  hub_url = "http://localhost:4444/wd/hub"
  DriverType = Literal["ErankKeywordScrapper"]
  
  @classmethod
  def get_driver(cls, __type: DriverType) -> WebdriverController:
    return cls.factories[__type](cls.hub_url)
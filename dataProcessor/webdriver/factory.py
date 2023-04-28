from typing import Self, Literal
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchWindowException

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

class WebdriverController:
  __slots__ = "_hub_url", "options", "driver", "session_id"
  
  def __init__(self, hub_url: str) -> None:
    self._hub_url = hub_url
    self.options = Options()
    self.set_options()
    self.driver = Remote(
      command_executor=self._hub_url,
      options=self.options,
    )
    self.session_id: str = self.driver.session_id # type: ignore
  
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

class ErankKeywordScrapper(WebdriverController):
  __slots__ = tuple()
  
  URL = "https://erank.com/"
  
  def __init__(self, hub_url: str) -> None:
    super().__init__(hub_url)
  
  def set_options(self):
    global DEFAULT_DRIVER_OPTIONS
    for option in DEFAULT_DRIVER_OPTIONS:
      self.options.add_argument(option)
  
  def initialize(self) -> None:
    pass

class WebdriverControllerFactory:
  factories = {
    "ErankKeywordScrapper": ErankKeywordScrapper
  }
  hub_url = "http://localhost:4444/wd/hub"
  DriverType = Literal["ErankKeywordScrapper"]
  
  @classmethod
  def get_driver(cls, __type: DriverType) -> WebdriverController:
    return cls.factories[__type](cls.hub_url)
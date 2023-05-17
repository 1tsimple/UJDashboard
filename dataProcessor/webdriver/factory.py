import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import logging
import asyncio
import threading
import pyperclip
import io
import csv
import json

from typing import Self, Literal, Any
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
from bs4 import BeautifulSoup, Tag
from utils.binaryTree import ErankNode, ERANK_DATA_KEYS


import time

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
    self.wait = WebDriverWait(self.driver, 10)
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
  
  def get_keyword_data(self, keyword) -> dict[str, list[list[str]]]: ...

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
  
  def initialize(self) -> None:
    self.driver.get(self.URL)
    self.__log_in()
  
  def __log_in(self) -> None:
    log_in_link = self.wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "Login")))
    log_in_link.click()
    
    email_input = self.wait.until(EC.visibility_of_element_located((By.ID, "signin-email")))
    email_input.send_keys(os.environ.get("erank_email"))
    
    password_input = self.wait.until(EC.visibility_of_element_located((By.ID, "signin-password")))
    password_input.send_keys(os.environ.get("erank_password"))
    
    log_in_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(),'Login')]")))
    log_in_button.click()
  
  def get_keyword_data(self, keyword: str) -> dict[str, dict[str, dict[str, str | int | float | None]]]:
    keyword_tool_data = self.__extract_keyword_research_data(keyword)
    keyword_research_data = self.__extract_keyword_tool_data(keyword)
    return {"keyword-tool-data": keyword_tool_data, "keyword-research-data": keyword_research_data}
  
  def __extract_keyword_research_data(self, keyword: str):
    keyword_research_url = f'{self.URL}keyword-explorer?keywords={keyword.replace(" ", "+")}&country=USA&source=etsy'
    soup = BeautifulSoup(self.__get_page_html(keyword_research_url), "lxml")
    tbody: Tag = soup.find("table").find("tbody") # type: ignore
    rows: list[Tag] = tbody.find_all("tr") # type: ignore
    data: list[list[str]] = list(map(lambda row: list(map(lambda x: x.text.lstrip().rstrip(), row.find_all("td"))), rows))
    clean_data = {}
    for row in data:
      print(row)
      clean_data[row[0]] = {
        ERANK_DATA_KEYS.word_count: len(row[0].split(" ")),
        ERANK_DATA_KEYS.average_searches: None if row[4] == "" or row[4] == "Unknown" else int(row[4].replace(",", "").replace("< 2", "")),
        ERANK_DATA_KEYS.average_clicks: None if row[5] == "" or row[5] == "Unknown" else int(row[5].replace(",", "").replace("< 2", "")),
        ERANK_DATA_KEYS.average_ctr: None if row[6].replace("%", "") == "" or row[6] == "Unknown" else int(row[6].replace("%", "").replace("< 2", "")),
        ERANK_DATA_KEYS.etsy_competition: None if row[7] == "" or row[7] == "Unknown" else int(row[7].replace(",", "").replace("< 2", "")),
        ERANK_DATA_KEYS.google_searches: None if row[8] == "" or row[8] == "Unknown" else int(row[8].replace(",", "").replace("< 2", "")),
        ERANK_DATA_KEYS.google_cpc: None if row[9] == "" or row[9] == "Unknown" else float(row[9]),
        ERANK_DATA_KEYS.long_tail: row[11],
      }
    return clean_data
  
  def __get_page_html(self, url: str) -> str:
    return self.driver.execute_script(f"""
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '{url}', false);
      xhr.send(null);
      return xhr.responseText;
    """)
  
  def __extract_keyword_tool_data(self, keyword: str) -> dict[str, dict[str, Any]]:
    _json = self.__get_keyword_tool_data_json(keyword)
    with open(os.path.join(SCRIPT_DIR, "tool_data.json"), mode="w", encoding="utf8") as f:
      json.dump(_json, f)
    clean_data = {}
    for kw_data in _json["keyword_ideas"]["all"]:
      clean_data[kw_data["keyword"]] = {
        ERANK_DATA_KEYS.word_count: len(kw_data["keyword"].split(" ")),
        ERANK_DATA_KEYS.average_searches: kw_data["avg_searches"]["order_value"],
        ERANK_DATA_KEYS.average_clicks: kw_data["avg_clicks"]["order_value"],
        ERANK_DATA_KEYS.average_ctr: kw_data["ctr"]["order_value"],
        ERANK_DATA_KEYS.etsy_competition: kw_data["competition"]["value"],
        ERANK_DATA_KEYS.google_searches: int(kw_data["google"]["avg_searches"].replace(",", "")) if kw_data["google"]["avg_searches"] != "" else None,
        ERANK_DATA_KEYS.google_cpc: float(kw_data["google"]["cpc"]) if kw_data["google"]["cpc"] != "" else None,
        ERANK_DATA_KEYS.long_tail: kw_data["longtail"]
      }
    return clean_data
  
  def __get_keyword_tool_data_json(self, keyword: str) -> dict[str, Any]:
    return json.loads(self.driver.execute_script(
      """
        let url = 'https://erank.com/keyword-tool';
        let data = {{
          'processFunc': 'etsyCall',
          'keyword': '{keyword}',
          'member_id': 1178565,
          'country': 'USA',
          'sort_on': 'score'
        }};
        let headers = {{
          'Content-Type': 'application/x-www-form-urlencoded',
          'Referer': 'https://erank.com/keyword-tool?keywords={keyword_query}&country=USA',
          'Origin': 'https://erank.com'
        }};
        let body = new URLSearchParams(data);
        return fetch(url, {{
          method: 'POST',
          headers: headers,
          body: body
        }}).then(response => {{
            if (!response.ok) {{
              throw new Error(`HTTP error! status: ${{response.status}}`);
            }}
            return response.text();
          }})
      """.format(keyword=keyword, keyword_query=keyword.replace(" ", "+"))
    ))

class WebdriverControllerFactory:
  factories = {
    "ErankKeywordScrapper": ErankKeywordScrapper
  }
  hub_url = "http://localhost:4444/wd/hub"
  DriverType = Literal["ErankKeywordScrapper"]
  
  @classmethod
  def get_driver(cls, __type: DriverType) -> WebdriverController:
    return cls.factories[__type](cls.hub_url)
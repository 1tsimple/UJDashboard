import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import logging
import json

from typing import Self, Literal, Any, Optional
from abc import ABC, abstractmethod

from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, validator, root_validator

from utils.binaryTree import ErankNode, ERANK_DATA_KEYS

# TODO: add average searches / competition ratio

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

from pydantic import BaseModel, validator
from typing import Optional, Literal

class ErankKeywordData(BaseModel):
  __slots__ = "keyword", "word_count", "character_count", "tag_occurrences", "average_searches", "average_clicks", "average_ctr", "average_csi", "etsy_competition", "google_searches", "google_cpc", "google_competition", "long_tail_keyword"

  keyword: str
  word_count: int = -1
  character_count: int = -1
  tag_occurrences: Optional[int]
  average_searches: Optional[int]
  average_clicks: Optional[int]
  average_ctr: Optional[float] = -1.0
  average_csi: Optional[float] = -1.0
  etsy_competition: Optional[int]
  google_searches: Optional[int]
  google_cpc: Optional[float]
  google_competition: Optional[float]
  long_tail_keyword: Literal["Yes", "Maybe", "No"]
  
  @validator("word_count", always=True)
  def calculate_word_count(cls, word_count):
    keyword = cls.keyword
    return len(keyword.split(" "))

  @validator("character_count", always=True)
  def calculate_character_count(cls, character_count):
    keyword = cls.keyword
    return len(keyword)

  @validator("average_ctr", always=True)
  def calculate_average_ctr(cls, average_ctr):
    average_searches = cls.average_searches
    average_clicks = cls.average_clicks
    if average_clicks is not None and average_searches is not None and average_searches != 0:
      return (average_clicks / average_searches) * 100
    return None
  
  @validator("average_csi", always=True)
  def calculate_average_csi(cls, average_csi):
    average_searches = cls.average_searches
    average_clicks = cls.average_clicks
    etsy_competition = cls.etsy_competition
    if average_clicks is not None and average_searches is not None and etsy_competition is not None and average_searches != 0:
      return (average_clicks / (average_searches * average_searches)) * etsy_competition
    return None

  @validator("average_searches", "average_clicks", "etsy_competition", "google_searches", "google_cpc", "google_competition", pre=True)
  def validate_field(cls, field_value):
    if field_value in ("", "Unknown", "< 20"):
      return None
    if "%" in field_value:
      field_value = field_value.replace("%", "")
    if "," in field_value:
      field_value = field_value.replace(",", "")
    return field_value

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
    keyword_research_data = self.__extract_keyword_research_data(keyword)
    keyword_tool_data = self.__extract_keyword_tool_data(keyword)
    
    return {"keyword-tool-data": keyword_tool_data, "keyword-research-data": keyword_research_data}
  
  def __extract_keyword_research_data(self, keyword: str):
    keyword_research_url = f'{self.URL}keyword-explorer?keywords={keyword.replace(" ", "+")}&country=USA&source=etsy'
    soup = BeautifulSoup(self.__get_page_html(keyword_research_url), "lxml")
    tbody: Tag = soup.find("table").find("tbody") # type: ignore
    rows: list[Tag] = tbody.find_all("tr") # type: ignore
    data: list[list[Any]] = list(map(lambda row: list(map(lambda x: x.text.lstrip().rstrip(), row.find_all("td"))), rows))
    
    return [
      ErankKeywordData( 
        keyword = row[0],
        tag_occurrences = None,
        average_searches = row[4],
        average_clicks = row[5],
        etsy_competition = row[7],
        google_searches = row[8],
        google_cpc = row[9],
        google_competition = row[10],
        long_tail_keyword = row[11]
      ).dict()
      for row in data
    ]
  
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
        ERANK_DATA_KEYS.tag_occurrences: kw_data["occurences"],
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
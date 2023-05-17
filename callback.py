import dash
import json
import asyncio
import pandas as pd
from dash import Input, Output, State, ALL, MATCH, ctx
from dash.exceptions import PreventUpdate
from typing import Any, Literal
from enum import Enum, StrEnum
from collections import defaultdict

from database.dBManager import DBManager
from dataProcessor.graphFactory import GraphFactory
from dataProcessor.webdriver.manager import DriverControllerManager
from dataProcessor.webdriver.factory import WebdriverControllerFactory

from components.erankKeyword import get_keyword_data_container
from utils.binaryTree import ERANK_DATA_KEYS

class FilterState(Enum):
  VISIBLE = {
    "borderColor": "var(--bg-blue)",
    "boxShadow": "0"
  }
  HIDDEN = {
    "borderColor": "var(--bg-grey)",
    "boxShadow": "0px 0px 0px 3px var(--bg-blue-alpha)"
  }

Marketplace = {
  "Amazon.ca": "Canada",
  "Amazon.com": "United States"
}

def str_to_int(text: str, default_value=None, type: Literal["int", "float"]="int") -> int | float | None:
  try:
    if type == "int":
      number = int(text)
    else:
      number = float(text)
  except ValueError:
    number = default_value
  return number

class CallbackManager():
  __slots__ = "app", "db", "driver_manager", "driver_factory"
  def __init__(self, app: dash.Dash, database: DBManager, driver_manager: DriverControllerManager, driver_factory: WebdriverControllerFactory) -> None:
    self.app = app
    self.db = database
    self.driver_manager = driver_manager
    self.driver_factory = driver_factory
  
  def init_callbacks(self) -> None:
    # Home Page
    self.refresh_product_filter()
    self.get_product_sales()
    self.update_product_filters_options()
    self.update_graphs()
    
    # Etsy Page
    self.start_erank_crawl_session()
    self.check_erank_crawler_status()
    self.extract_keyword_data()
    self.filter_keyword_data()
    self.update_filtered_keywords_html()
    
  
  def refresh_product_filter(self) -> None:
    @self.app.callback(
      Output({"type": "product-filter", "uuid": ALL}, "options"),
      Input("refresh-dropdown-options", "n_intervals")
    )
    def callback(interval):
      return [self.db.puller.get_product_options() for _ in range(len(ctx.outputs_list))]
  
  def get_product_sales(self) -> None:
    @self.app.callback(
      Output({"type": "graph-data-storage", "uuid": MATCH}, "data"),
      Input({"type": "product-filter", "uuid": MATCH}, "value"),
      prevent_initial_call=True
    )
    def callback(SKUs: str):
      return self.db.puller.get_product_sales(json.loads(SKUs))
  
  def update_product_filters_options(self) -> None:
    @self.app.callback(
      Output({"type": "marketplace-filter", "uuid": MATCH}, "options"),
      Output({"type": "variant-filter", "uuid": MATCH}, "options"),
      Output({"type": "groupby-filter", "uuid": MATCH}, "options"),
      Output({"type": "marketplace-filter", "uuid": MATCH}, "value"),
      Output({"type": "variant-filter", "uuid": MATCH}, "value"),
      Output({"type": "groupby-filter", "uuid": MATCH}, "value"),
      Output({"type": "date-filter", "uuid": MATCH}, "max"),
      Output({"type": "date-filter", "uuid": MATCH}, "value"),
      Output({"type": "date-filter", "uuid": MATCH}, "marks"),
      Output({"type": "graph-time-frame-data-storage", "uuid": MATCH}, "data"),
      Input({"type": "graph-data-storage", "uuid": MATCH}, "data"),
      prevent_initial_call=True
    )
    def callback(data: list[dict[str, str]]):
      unique_dict = self._get_unique_values_in_dict(data)
      marketplaces = unique_dict["MarketplaceName"]
      variant_categories = [value for key, value in unique_dict.items() if "Variant." in key]
      marketplace_options = [{"label": Marketplace[marketplace], "value": marketplace} for marketplace in marketplaces if marketplace is not None]
      variant_options = [{"label": variant, "value": variant} for category in variant_categories for variant in category if variant is not None]
      groupby_options = [{"label": "None", "value": None}, {"label": "Marketplace", "value": "Marketplace", "disabled": True}, {"label": "Variant", "value": "Variant", "disabled": True}]
      if len(marketplace_options) >= 2:
        groupby_options[1] = {"label": "Marketplace", "value": "Marketplace"}
      if len(variant_options) >= 2:
        groupby_options[2] = {"label": "Variant", "value": "Variant"}
      get_values = lambda option_list: [option["value"] for option in option_list]
      dates = pd.to_datetime(pd.Series(map(lambda x: x.split("T")[0], unique_dict["PostedDate"])))
      dates = pd.date_range(dates.min(), dates.max(), name="PostedDate")
      marks = {index[0]: date.strftime("%B %Y") for index, date, condition in zip(enumerate(dates), dates, dates.is_month_start) if condition}
      return marketplace_options, variant_options, groupby_options, get_values(marketplace_options), get_values(variant_options), None, len(dates), (0, len(dates)), marks, dates.to_list()
  
  @staticmethod
  def _get_unique_values_in_dict(dict_list: list[dict[Any, Any]]) -> defaultdict[Any, set[Any]]:
    unique_dict = defaultdict(set)
    for dict_ in dict_list:
      for key, value in dict_.items():
        unique_dict[key].add(value)
    return unique_dict
  
  def update_graphs(self) -> None:
    @self.app.callback(
      Output({"type": "main-graph", "uuid": MATCH}, "figure"),
      State({"type": "graph-data-storage", "uuid": MATCH}, "data"),
      Input({"type": "filter-apply-button", "uuid": MATCH}, "n_clicks"),
      State({"type": "marketplace-filter", "uuid": MATCH}, "value"),
      State({"type": "variant-filter", "uuid": MATCH}, "value"),
      Input({"type": "groupby-filter", "uuid": MATCH}, "value"),
      Input({"type": "date-filter", "uuid": MATCH}, "value"),
      State({"type": "graph-time-frame-data-storage", "uuid": MATCH}, "data"),
      prevent_initial_call=True
    )
    def callback(data: list[dict[str, Any]], button_click: int, marketplaces: list[str], variants: list[str], groupby: str|None, date_indexes: tuple[int, int], dates: list[str]):
      dataframe = pd.DataFrame(data)
      graph = GraphFactory().get_graph(
        type_="total_sales_count",
        dataframe=dataframe,
        marketplaces=marketplaces,
        variants=variants,
        groupby=groupby,
        time_frame=dates[date_indexes[0]:date_indexes[1]]
      )
      return graph
  
  def start_erank_crawl_session(self) -> None:
    @self.app.callback(
      Output("erank-crawler-session-id", "data"),
      #Output("erank-iframe", "srcDoc"),
      Input("erank-crawler-start-button", "n_clicks"),
      State("erank-crawler-session-id", "data"),
      prevent_initial_call=True
    )
    def callback(click: int, session_id: None | str):
      if session_id is None:
        crawler = self.driver_factory.get_driver("ErankKeywordScrapper")
      else:
        crawler = self.driver_manager.driver_controllers.get(session_id)
      if crawler is None:
        crawler = self.driver_factory.get_driver("ErankKeywordScrapper")
      crawler.initialize()
      self.driver_manager.add_controller(crawler)
      return crawler.session_id#, crawler.get_page_source()
  
  def check_erank_crawler_status(self) -> None:
    @self.app.callback(
      Output("crawler-status-msg", "children"),
      Output("crawler-status-icon", "className"),
      Output("erank-status-spinner", "color"),
      Output("crawler-status-msg", "style"),
      Output("crawler-status-icon", "style"),
      Input("erank-crawler-status-checker", "n_intervals"),
      State("erank-crawler-session-id", "data")
    )
    def callback(interval: int, session_id: str|None):
      if session_id is None:
        return "Crawler is disconnected!", "fa-solid fa-circle-xmark", "red", {"color": "red"}, {"color": "red"}
      else:
        if self.driver_manager.driver_controllers.get(session_id) is None:
          return "Crawler is disconnected!", "fa-solid fa-circle-xmark", "red", {"color": "red"}, {"color": "red"}
        return "Crawler is connected!", "fa-solid fa-circle-check", "green", {"color": "green"}, {"color": "green"}
  
  def extract_keyword_data(self) -> None:
    @self.app.callback(
      Output("erank-keyword-data-raw", "data"),
      Input("erank-search-button", "n_clicks"),
      State("erank-search-bar", "value"),
      Input("erank-search-bar", "n_submit"),
      State("erank-crawler-session-id", "data"),
      prevent_initial_call=True
    )
    def callback(click: int, keyword: str, submit: int, session_id: str):
      crawler = self.driver_manager.driver_controllers.get(session_id)
      if crawler is None:
        raise PreventUpdate
      return crawler.get_keyword_data(keyword)
  
  def filter_keyword_data(self) -> None:
    @self.app.callback(
      Output("erank-keyword-data-filtered", "data"),
      Input("erank-keyword-data-raw", "data"),
      Input("min-character-count", "value"),
      Input("max-character-count", "value"),
      Input("min-tag-occurrences", "value"),
      Input("max-tag-occurrences", "value"),
      Input("min-average-searches", "value"),
      Input("max-average-searches", "value"),
      Input("min-average-clicks", "value"),
      Input("max-average-clicks", "value"),
      Input("min-average-ctr", "value"),
      Input("max-average-ctr", "value"),
      Input("min-etsy-competition", "value"),
      Input("max-etsy-competition", "value"),
      Input("min-google-searches", "value"),
      Input("max-google-searches", "value"),
      Input("min-google-cpc", "value"),
      Input("max-google-cpc", "value"),
      prevent_initial_call=True
    )
    def callback(
      data: dict[str, dict[str, dict[str, str | int | float | None]]],
      min_character_count: int|None, max_character_count: int|None,
      min_tag_occurrences: int|None, max_tag_occurrences: int|None,
      min_average_searches: int|None, max_average_searches: int|None,
      min_average_clicks: int|None, max_average_clicks: int|None,
      min_average_ctr: int|None, max_average_ctr: int|None,
      min_etsy_competition: int|None, max_etsy_competition: int|None,
      min_google_searches: int|None, max_google_searches: int|None,
      min_google_cpc: int|None, max_google_cpc: int|None
    ):
      all_data = data["keyword-research-data"] | data["keyword-tool-data"]
      __filter = {
        ERANK_DATA_KEYS.word_count: (min_character_count, max_character_count),
        ERANK_DATA_KEYS.tag_occurrences: (min_tag_occurrences, max_tag_occurrences),
        ERANK_DATA_KEYS.average_searches: (min_average_searches, max_average_searches),
        ERANK_DATA_KEYS.average_clicks: (min_average_clicks, max_average_clicks),
        ERANK_DATA_KEYS.average_ctr: (min_average_ctr, max_average_ctr),
        ERANK_DATA_KEYS.etsy_competition: (min_etsy_competition, max_etsy_competition),
        ERANK_DATA_KEYS.google_searches: (min_google_searches, max_google_searches),
        ERANK_DATA_KEYS.google_cpc: (min_google_cpc, max_google_cpc),
        ERANK_DATA_KEYS.long_tail: None
      }
      return self.__filter_data(all_data, __filter)
  
  @staticmethod
  def __filter_data(__data: dict[str, dict[str, str|int|float|None]], __filter: dict[str, tuple[int|None, int|None]]) -> dict[str, dict[str, str|int|float|None]]:
    filtered = __data.copy()
    for keyword, data in __data.items():
      for filter_key, value in data.items():
        if value is None:
          continue
        if filter_key == "long_tail_keyword":
          if __filter[filter_key] is not None and value != __filter[filter_key]:
            del filtered[keyword]
            break
          continue
        _min, _max = __filter[filter_key]
        if (_min is not None and _min >= value) or (_max is not None and _max <= value): # type: ignore
          del filtered[keyword]
          break
    return filtered
  
  def update_filtered_keywords_html(self) -> None:
    @self.app.callback(
      Output("erank-data-container", "children"),
      Input("erank-keyword-data-filtered", "data"),
      prevent_initial_call=True
    )
    def callback(data):
      return [
        get_keyword_data_container(
          keyword=keyword,
          character_count=_data["character_count"],
          tag_occurrences=_data["tag_occurrences"],
          average_searches=_data["average_searches"],
          average_clicks=_data["average_clicks"],
          average_ctr=_data["average_ctr"],
          etsy_competition=_data["etsy_competition"],
          google_searches=_data["google_searches"],
          google_cpc=_data["google_cpc"],
          long_tail_keyword=_data["long_tail_keyword"]
        )
        for keyword, _data in data.items()
      ]
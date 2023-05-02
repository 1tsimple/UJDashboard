import dash
import json
import pandas as pd
from dash import Input, Output, State, ALL, MATCH, ctx
from dash.exceptions import PreventUpdate
from typing import Any
from enum import Enum, StrEnum
from collections import defaultdict

from database.dBManager import DBManager
from dataProcessor.graphFactory import GraphFactory
from dataProcessor.webdriver.manager import DriverControllerManager
from dataProcessor.webdriver.factory import WebdriverControllerFactory
#from dataProcessor.etsy.erankCrawler import CrawlerManager

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
    #self.start_erank_crawl_session()
    #self.extract_keyword_data()
  
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
      Output("crawler-session-id", "data"),
      Output("erank-iframe", "srcDoc"),
      Input("crawler-start-button", "n_clicks"),
      State("crawler-session-id", "data"),
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
      return crawler.session_id, crawler.get_page_source()
  
  def extract_keyword_data(self) -> None:
    @self.app.callback(
      Output("crawler-keyword-input", "value"),
      Input("crawler-extract-button", "n_clicks"),
      State("crawler-keyword-input", "value"),
      prevent_initial_call=True
    )
    def callback(click: int, keyword: str):
      print(keyword)
      return keyword
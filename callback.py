import dash
import json
from dash import Input, Output, State, ALL, MATCH, ctx
from typing import Any
from enum import Enum, StrEnum
from collections import defaultdict

from database.dBManager import DBManager

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
  def __init__(self, app: dash.Dash) -> None:
    self.app = app
    self.db = DBManager()
  
  def init_callbacks(self):
    #self.refresh_product_filter() # currently bugged due to pattern-matching update bug in dash
    self.toggle_filter()
    self.get_product_sales()
    self.update_product_filters_options()
    self.update_graphs()
  
  def refresh_product_filter(self):
    @self.app.callback(
      Output({"type": "product-filter", "uuid": ALL}, "options"),
      Input("refresh-dropdown-options", "n_intervals")
    )
    def callback(interval):
      return [self.db.puller.get_product_options() for _ in range(len(ctx.outputs_list))]
  
  def toggle_filter(self):
    @self.app.callback(
      Output({"type": "filter", "uuid": MATCH}, "style"),
      Output({"type": "filter-button", "uuid": MATCH}, "style"),
      Input({"type": "filter-button", "uuid": MATCH}, "n_clicks"),
      Input({"type": "filter-apply-button", "uuid": MATCH}, "n_clicks"),
      State({"type": "filter", "uuid": MATCH}, "style"),
      prevent_initial_call=True
    )
    def callback(filter_button_click: int, apply_button_click: int, style: dict[str, str]):
      if ctx.triggered_id == "filter-apply-button":
        style["overflow"] = "hidden"
        filter_style = FilterState.HIDDEN.value
      elif style["overflow"] == "hidden":
        style["overflow"] = "visible"
        filter_style = FilterState.VISIBLE.value
      else:
        style["overflow"] = "hidden"
        filter_style = FilterState.HIDDEN.value
      return style, filter_style
  
  def get_product_sales(self):
    @self.app.callback(
      Output({"type": "graph-data-storage", "uuid": MATCH}, "data"),
      Input({"type": "product-filter", "uuid": MATCH}, "value"),
      prevent_initial_call=True
    )
    def callback(SKUs: str):
      return self.db.puller.get_product_sales(json.loads(SKUs))
  
  def update_product_filters_options(self):
    @self.app.callback(
      Output({"type": "marketplace-filter", "uuid": MATCH}, "options"),
      Output({"type": "variant-filter", "uuid": MATCH}, "options"),
      Output({"type": "groupby-filter", "uuid": MATCH}, "options"),
      Output({"type": "marketplace-filter", "uuid": MATCH}, "value"),
      Output({"type": "variant-filter", "uuid": MATCH}, "value"),
      Output({"type": "groupby-filter", "uuid": MATCH}, "value"),
      Input({"type": "graph-data-storage", "uuid": MATCH}, "data"),
      prevent_initial_call=True
    )
    def callback(data: list[dict[str, str]]):
      unique_dict = self._get_unique_values_in_dict(data)
      marketplaces = unique_dict["MarketplaceName"]
      variant_categories = [value for key, value in unique_dict.items() if "Variant." in key]
      marketplace_options = [{"label": Marketplace[marketplace], "value": marketplace} for marketplace in marketplaces if marketplace is not None]
      variant_options = [{"label": variant, "value": variant} for category in variant_categories for variant in category if variant is not None]
      groupby_options = [{"label": "None", "value": None}, {"label": "Marketplace", "value": "MarketplaceName", "disabled": True}, {"label": "Variant", "value": "Variant", "disabled": True}]
      if len(marketplace_options) >= 2:
        groupby_options[1] = {"label": "Marketplace", "value": "MarketplaceName"}
      if len(variant_options) >= 2:
        groupby_options[2] = {"label": "Variant", "value": "Variant"}
      def get_values(option_list: list[dict[str, str]]) -> list[str]:
        return [value for option in option_list for key, value in option.items()]
      return marketplace_options, variant_options, groupby_options, get_values(marketplace_options), get_values(variant_options), None
  
  @staticmethod
  def _get_unique_values_in_dict(dict_list: list[dict[Any, Any]]) -> defaultdict[Any, set[Any]]:
    unique_dict = defaultdict(set)
    for dict_ in dict_list:
      for key, value in dict_.items():
        unique_dict[key].add(value)
    return unique_dict
  
  def update_graphs(self):
    @self.app.callback(
      Output({"type": "main-graph", "uuid": MATCH}, "figure"),
      Input({"type": "filter-apply-button", "uuid": MATCH}, "n_clicks"),
      State({"type": "marketplace-filter", "uuid": MATCH}, "value"),
      State({"type": "variant-filter", "uuid": MATCH}, "value"),
      Input({"type": "groupby-filter", "uuid": MATCH}, "value"),
      prevent_initial_call=True
    )
    def callback(button_click: int, marketplace, variant: list[str], groupby: str|None):
      return {}
from typing import Any
from enum import Enum, StrEnum
from collections import defaultdict
from dash import ctx

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

def toggle_filter(style: dict[str, str]):
  style_copy = style.copy()
  if ctx.triggered_id == "filter-apply-button":
    style_copy["overflow"] = "hidden"
    filter_style = FilterState.HIDDEN.value
  elif style_copy["overflow"] == "hidden":
    style_copy["overflow"] = "visible"
    filter_style = FilterState.VISIBLE.value
  else:
    style_copy["overflow"] = "hidden"
    filter_style = FilterState.HIDDEN.value
  return style_copy, filter_style

def get_product_filters_options(data: list[dict[str, str]]):
  unique_dict = get_unique_values_in_dict(data)
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

def get_unique_values_in_dict(dict_list: list[dict[Any, Any]]) -> defaultdict[Any, set[Any]]:
  unique_dict = defaultdict(set)
  for dict_ in dict_list:
    for key, value in dict_.items():
      unique_dict[key].add(value)
  return unique_dict
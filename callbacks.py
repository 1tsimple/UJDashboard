from enum import Enum
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

def toggle_filter(style: dict[str, str]):
  style_copy = style.copy()
  if ctx.triggered_id["type"] == "filter-apply-button":
    style_copy["overflow"] = "hidden"
    filter_style = FilterState.HIDDEN.value
  elif style_copy["overflow"] == "hidden":
    style_copy["overflow"] = "visible"
    filter_style = FilterState.VISIBLE.value
  else:
    style_copy["overflow"] = "hidden"
    filter_style = FilterState.HIDDEN.value
  return style_copy, filter_style
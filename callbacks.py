from dash import ctx

def toggle_filter(style: dict[str, str]):
  style_copy = style.copy()
  if ctx.triggered_id["type"] == "filter-apply-button":
    style_copy["overflow"] = "hidden"
  elif style_copy["overflow"] == "hidden":
    style_copy["overflow"] = "visible"
  else:
    style_copy["overflow"] = "hidden"
  return style_copy
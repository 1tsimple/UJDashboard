# ---------- SETUP ----------
import os, logging, sys
from datetime import date
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, f"logs/{date.today()}.log"))
logging.basicConfig(
  level=logging.INFO,
  format="[ %(asctime)s ] - %(thread)d - %(filename)s - %(funcName)s - [ %(levelname)s ] - %(message)s",
  datefmt="%Y-%m-%d %H:%M:%S",
  filename=LOG_DIR
)

# ---------- IMPORTS ----------

import dash
import dash_bootstrap_components as dbc
#from dash_extensions.enrich import Trigger
from dash import html, dcc, Input, Output, State, ALL, MATCH, ctx

from components.header import get_header
from components.footer import get_footer
from callbacks import *

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
server = app.server

app.layout = html.Div(id="main-body", children=[
  html.Header(children=get_header()),
  dash.page_container,
  html.Footer(id="footer-container", children=get_footer()),
])

@app.callback(
  Output({"type": "filter", "uuid": MATCH}, "style"),
  Output({"type": "filter-button", "uuid": MATCH}, "style"),
  Input({"type": "filter-button", "uuid": MATCH}, "n_clicks"),
  Input({"type": "filter-apply-button", "uuid": MATCH}, "n_clicks"),
  State({"type": "filter", "uuid": MATCH}, "style"),
  prevent_initial_call=True
)
def toggle_filter_callback(filter_button_click: int, apply_button_click: int, style: dict[str, str]):
  return toggle_filter(style)

from database.dBManager import DBManager

db = DBManager()

@app.callback(
  Output({"type": "product-filter", "uuid": ALL}, "options"),
  Input("refresh-dropdown-options", "n_intervals")
)
def refresh_product_options(interval):
  return [db.puller.get_product_options() for _ in range(len(ctx.outputs_list))]

@app.callback(
  Output({"type": "graph-data-storage", "uuid": MATCH}, "data"),
  Input({"type": "product-filter", "uuid": MATCH}, "value"),
  prevent_initial_call=True
)
def get_product_SKUs(value):
  print(value)
  return None

if __name__ == "__main__":
  app.run(debug=True)
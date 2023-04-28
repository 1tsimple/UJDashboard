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
import json
from dash import html, dcc, Input, Output, State, ALL, MATCH, ctx

from components.header import get_header
from components.footer import get_footer
from database.dBManager import DBManager
from dataProcessor.webdriver.manager import DriverControllerManager
from dataProcessor.webdriver.factory import WebdriverControllerFactory
from callback import CallbackManager

def setup(app: dash.Dash):
  db = DBManager()
  dm = DriverControllerManager()
  dm.start()
  cbm = CallbackManager(app, db, dm, WebdriverControllerFactory())
  cbm.init_callbacks()

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
server = app.server

app.layout = html.Div(id="main-body", children=[
  html.Header(children=get_header()),
  dash.page_container,
  html.Footer(id="footer-container", children=get_footer()),
])

if __name__ == "__main__":
  setup(app)
  app.run(host="0.0.0.0", debug=True)
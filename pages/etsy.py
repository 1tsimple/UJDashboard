import dash
from dash import dcc, html

dash.register_page(__name__)

layout = html.Section(id="erank-container", children=[
  html.H1("Etsy Page")
])
import dash
import uuid
from dash import dcc, html

dash.register_page(__name__, path="/")

from components.graph import get_graph

layout = html.Section(id="homepage-container", children=[
  html.Div(id="content-container", children=[
    html.Div(id="all-graphs-container", children=[
      get_graph(uuid.uuid4())
    ]),
    html.Div(id="add-button-wrapper", children=[
      html.Button(id="graph-add-button", children=[
        html.Div(id="add-button-text-wrapper", children=[
          html.Span(children="_____"),
          html.Span(children="_____")
        ])
      ])
    ])
  ])
])
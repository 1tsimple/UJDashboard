import dash
import dash_bootstrap_components as dbc
from dash import html, dcc



def get_graph():
  return html.Div(id="graph-container-outer", className="graph-container-outer", children=[
    html.Div(id="close-button-wrapper", className="close-button-wrapper", children=[
      html.Button(id={"type": "graph-close-button"}, className="graph-close-button", children=[
        html.Div(id="close-button-text-wrapper", className="close-button-text-wrapper", children=[
          html.Span(children="+")
        ])
      ])
    ]),
    html.Div(id="filter-container", className="filter-container", children=[
      dcc.Dropdown(
        id={"type": "product-filter"},
        placeholder="Select a product",
        clearable=False,
      ),
      html.Div(id="filter", className="filter", children=[
        html.Button(id={"type": "filter-button"}, className="filter-button", children=[
          html.Span(children="Filter")
        ]),
      ]),
      html.Div(className="groupby-filter-wrapper", children=[
        html.Span(children="Group By"),
        dbc.RadioItems(
          id={"type": "groupby-filter"},
          className="groupby-filter",
          options=[
            {"label": "None", "value": None},
            {"label": "Marketplace", "value": "value1"},
            {"label": "Listing", "value": "value2"},
            {"label": "Variant", "value": "value3"},
          ],
          label_checked_style={"color": "black"},
          value=None
        )
      ])
    ]),
    html.Div(id="graph-container-inner", className="graph-container-inner", children=[
      html.Div(id="graph-container", className="graph-container", children=[
        dcc.Loading(className="graph-loading", children=[
          dcc.Graph(
            figure={}
          )
        ])
      ]),
      html.Div(id="static-graph-container", className="static-graph-container", children=[
        
      ])
    ]),
    html.Div(id="date-slider-container", className="date-slider-container", children=[
      dcc.Slider()
    ])
  ])
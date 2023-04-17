import dash
import dash_bootstrap_components as dbc
import uuid
from dash import html, dcc

from database.dBManager import DBManager

db = DBManager()

def get_graph(uuid: uuid.UUID):
  uuid = str(uuid) # type: ignore
  return html.Div(className="graph-container-outer", children=[
    html.Div(className="close-button-wrapper", children=[
      html.Button(id={"type": "graph-close-button", "uuid": uuid}, className="graph-close-button", children=[
        html.Div(className="close-button-text-wrapper", children=[
          html.Span(children="+"),
          html.Div(className="clickable-close-button-dummy")
        ])
      ])
    ]),
    html.Div(className="filter-container", children=[
      dcc.Dropdown(
        id={"type": "product-filter", "uuid": uuid},
        options=db.puller.get_product_options(),
        placeholder="Select a product",
        clearable=False,
      ),
      dcc.Interval(id="refresh-dropdown-options", interval=5000, n_intervals=0),
      html.Div(id={"type": "filter", "uuid": uuid}, className="filter", children=[
        dbc.ButtonGroup(
          id={"type": "button-group-filter", "uuid": uuid},
          className="button-group-filter",
          children=[
            dbc.Button(
              className="filter-button",
              type="button",
              outline=True,
              color="grey",
              children="Filter"
            ),
            dbc.Button(
              id={"type": "filter-apply-button", "uuid": uuid},
              className="filter-apply-button",
              type="submit",
              outline=True,
              color="grey",
              children=html.I(className="fa-solid fa-check")
            ),
          ]
        ),
        dbc.Collapse(className="marketplace-collapse", is_open=True, children=[
          dbc.Card(children=[
            dcc.Loading(className="marketplace-loading", type="dot", children=[
              dcc.Dropdown(
                id={"type": "marketplace-filter", "uuid": uuid},
                placeholder="Select marketplaces",
                clearable=False,
                multi=True,
              )
            ]),
            dcc.Loading(className="variant-loading", type="dot", children=[
              dcc.Dropdown(
                id={"type": "variant-filter", "uuid": uuid},
                placeholder="Select variants",
                clearable=False,
                multi=True
              )
            ])
          ]),
        ])
      ]),
      html.Div(className="groupby-filter-wrapper", children=[
        html.Span(children="Group By"),
        dcc.Loading(id={"type": "radio-items-loading", "uuid": uuid}, type="dot", style={"position": "absolute", "top": "calc(100% + 4px)"}, children=[
          dbc.RadioItems(
            id={"type": "groupby-filter", "uuid": uuid},
            className="groupby-filter",
            options=[
              {"label": "None", "value": None},
              {"label": "Marketplace", "value": "Marketplace", "disabled": True},
              {"label": "Variant", "value": "Variant", "disabled": True},
            ],
            label_checked_style={"color": "var(--bg-blue)"},
            labelStyle={"color": "var(--text-black)"},
            value=None
          )
        ]),
      ])
    ]),
    html.Div(className="graph-container-inner", children=[
      html.Div(className="graph-container", children=[
        dcc.Loading(type="graph", className="graph-loading", children=[
          dcc.Graph(
            id={"type": "main-graph", "uuid": uuid},
            figure={}
          )
        ])
      ]),
      html.Div(className="static-graph-container", children=[
        
      ])
    ]),
    html.Div(className="date-slider-container", children=[
      #dcc.RangeSlider()
    ]),
    dcc.Store(id={"type": "graph-data-storage", "uuid": uuid}, modified_timestamp=-1)
  ])
import dash
import dash_bootstrap_components as dbc
import uuid
from dash import html, dcc



def get_graph(uuid: uuid.UUID):
  uuid = str(uuid)
  return html.Div(className="graph-container-outer", children=[
    html.Div(className="close-button-wrapper", children=[
      html.Button(id={"type": "graph-close-button", "uuid": uuid}, className="graph-close-button", children=[
        html.Div(className="close-button-text-wrapper", children=[
          html.Span(children="+")
        ])
      ])
    ]),
    html.Div(className="filter-container", children=[
      dcc.Dropdown(
        id={"type": "product-filter", "uuid": uuid},
        options=[
          {"label": "option1", "value": 1},
          {"label": "option2", "value": 2},
        ],
        placeholder="Select a product",
        clearable=False,
      ),
      html.Div(id={"type": "filter", "uuid": uuid}, className="filter", style={"overflow": "hidden"}, children=[
        html.Button(id={"type": "filter-button", "uuid": uuid}, className="filter-button", n_clicks=0, children=[
          html.Span(children="Filter")
        ]),
        html.Div(id={"type": "filter-expand", "uuid": uuid}, className="filter-expand", children=[
          html.Div(className="filter-dropdowns-wrapper", children=[
            dcc.Dropdown(
              id={"type": "marketplace-filter", "uuid": uuid},
              placeholder="Select marketplaces",
              clearable=False
            ),
            dcc.Dropdown(
              id={"type": "listing-filter", "uuid": uuid},
              placeholder="Select SKUs",
              clearable=False
            ),
            dcc.Dropdown(
              id={"type": "variant-filter", "uuid": uuid},
              placeholder="Select variants",
              clearable=False
            )
          ]),
          html.Button(id={"type": "filter-apply-button", "uuid": uuid}, className="filter-apply-button", n_clicks=0, children=[
            html.Span(children="Apply")
          ])
        ])
      ]),
      html.Div(className="groupby-filter-wrapper", children=[
        html.Span(children="Group By"),
        dbc.RadioItems(
          id={"type": "groupby-filter", "uuid": uuid},
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
    html.Div(className="graph-container-inner", children=[
      html.Div(className="graph-container", children=[
        dcc.Loading(className="graph-loading", children=[
          dcc.Graph(
            id={"uuid": uuid},
            figure={}
          )
        ])
      ]),
      html.Div(className="static-graph-container", children=[
        
      ])
    ]),
    html.Div(className="date-slider-container", children=[
      #dcc.Slider()
    ])
  ])
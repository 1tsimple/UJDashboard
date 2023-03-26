import dash
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
        dcc.Checklist(
          id={"type": "groupby-filter"},
          className="groupby-filter",
          options=[
            {"label": [html.Div(className="groupby-label-wrapper", children=html.Span(className="groupby-label", children="Marketplace"))], "value": "value1"},
            {"label": [html.Div(className="groupby-label-wrapper", children=html.Span(className="groupby-label", children="Listing"))], "value": "value2"},
            {"label": [html.Div(className="groupby-label-wrapper", children=html.Span(className="groupby-label", children="Variant"))], "value": "value3"},
          ],
          labelStyle={"display": "flex", "position": "relative"}
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
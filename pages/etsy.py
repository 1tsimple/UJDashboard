import dash
from dash import dcc, html
import dash_bootstrap_components as dbc


dash.register_page(__name__)

get_filters = lambda : [div for div in __get_filters(
  ids=("character-count", "average-searches", "average-clicks", "average-ctr", "etsy-competition", "google-searches", "google-cpc"),
  types=("number", "number", "number", "number", "number", "number", "number"),
  mins=(0, 0, 0, 0, 0, 0, 0),
  steps=(1, 100, 100, 1, 1000, 1000, 1)
)]

def __get_filters(ids: tuple[str, ...], types: tuple[str, ...], mins: tuple[int, ...], steps: tuple[int, ...]):
  for id_, type_, min_, step in zip(ids, types, mins, steps):
    yield html.Div(id=f"{id_}-container", children=[
      html.Span(f"{id_.replace('-', ' ')}"),
      html.Div(id=f"{id_}-filter", className="mix-max-filter", children=[
        dbc.Input(
          id=f"min-{id_}",
          type=type_,
          min=min_,
          step=step,
          size="sm",
          placeholder="min"
        ),
        dbc.Input(
          id=f"max-{id_}",
          type=type_,
          min=min_,
          step=step,
          size="sm",
          placeholder="max"
        )
      ])
    ])
  yield html.Div(id="longtail-filter", children=[
    
  ])

layout = html.Div(id="content-container", children=[
  html.Div(id="erank-data-container", children=[
    html.Div(id="erank-filter-container", children=[
      html.Div(id="etsy-button-container", children=[
        html.Button(id="crawler-starter", children="Start"),
        html.Button(id="data-extractor", children="Extract Data"),
        html.Button(id="apply-button", children="Apply")
      ]),
      html.Div(id="erank-filters", children=get_filters())
    ]),
    html.Div(id="erank-data-wrapper", children=[
      
    ])
  ])
])
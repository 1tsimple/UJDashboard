import dash
from dash import dcc, html
import dash_bootstrap_components as dbc


dash.register_page(__name__)

get_filters = lambda : [div for div in __get_filters(
  ids=("word-count", "tag-occurrences", "average-searches", "average-clicks", "average-ctr", "etsy-competition", "google-searches", "google-cpc"),
  types=("number", "number", "number", "number", "number", "number", "number", "number"),
  mins=(0, 0, 0, 0, 0, 0, 0, 0),
  steps=(1, 1, 100, 100, 1, 1000, 1000, 1)
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
  yield html.Div(id="longtail-filter")

layout = html.Div(id="content-container", children=[
  html.Div(id="content-container-inner", children=[
    html.Div(id="erank-crawler-control", children=[
      html.Div(id="search-bar-container", children=[
        dbc.Input(
          id="erank-search-bar",
          size="sm",
          placeholder="Search"
        ),
        html.Button(
          id="erank-search-button",
          children=html.I(
            id="erank-search-icon",
            className="fa-solid fa-magnifying-glass"
          )
        )
      ]),
      html.Div(id="crawler-status-container", children=[
        html.Div(id="crawler-status", children=[
          dbc.Spinner(id="erank-status-spinner", color="red", size="sm", children=[
            html.I(
              id="crawler-status-icon",
              style={"color": "red"},
              className="fa-solid fa-circle-xmark"
            )
          ]),
          html.Span(id="crawler-status-msg", style={"color": "red"}, children="Crawler is disconnected!"),
          dcc.Interval(id="erank-crawler-status-checker", interval=3000)
        ]),
        dbc.Button(
          id="erank-crawler-start-button",
          size="sm",
          children="Start",
          color="grey",
          outline=True
        ),
        dcc.Store(id="erank-crawler-session-id", storage_type="session")
      ])
    ]),
    html.Div(id="erank-filter-container", children=[
      html.Div(id="erank-filters", children=get_filters())
    ]),
    html.Div(id="erank-data-wrapper", children=[
      dcc.Store("erank-keyword-data-raw", storage_type="session"),
      dcc.Store("erank-keyword-data-filtered", storage_type="session"),
      html.Div(children=[
        html.Ul(className="nav nav-tabs", children=[
          html.Div(className="nav-item", children=[
            html.Button(className="nav-link", children=[
              html.Span(style={"color": "var(--bs-nav-tabs-link-active-color)"}, children=col_name),
              html.I(style={"color": "var(--bs-nav-tabs-link-active-color)"})
            ])
          ])
          for col_name in ("keywords", "tag occurrences", "average searches", "average clicks", "average ctr", "average csr", "etsy competition", "google searches", "google cpc", "long tail keyword")
        ]),
        dcc.Loading(id="erank-data-container", children=[
          dbc.Alert(
            id={"type": "erank-keyword-data-card", "id": "keyword"},
            className="erank-keyword-data-card",
            children=[
              html.Div(className="erank-keyword-wrapper", children=html.Span("tshirt")),
              html.Div(className="erank-tag-occurrences-wrapper", children=html.Span("1")),
              html.Div(className="erank-average-searches-wrapper", children=html.Span("76437")),
              html.Div(className="erank-average-clicks-wrapper", children=html.Span("78288")),
              html.Div(className="erank-average-ctr-wrapper", children=html.Span("102")),
              html.Div(className="erank-average-csi-wrapper", children=html.Span("0")),
              html.Div(className="erank-etsy-competition-wrapper", children=html.Span("0")),
              html.Div(className="erank-google-searches-wrapper", children=html.Span("0")),
              html.Div(className="erank-google-cpc-wrapper", children=html.Span("0")),
              html.Div(className="erank-long-tail-keyword-wrapper", children=html.Span("No")),
              html.Button(id={"type": "erank-keyword-data-card-close-button", "id": "tshirt"}, type="button", className="btn-close")
            ]
          )
        ])
      ]),
      html.Div(id="erank-data-container-removed", children=[
        
      ]),
    ])
  ])
])
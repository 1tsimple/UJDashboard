import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from typing import Any
from utils.templates import ErankFilterQuery

dash.register_page(__name__)

def get_min_max_filter(id_, min_ = 0, step = 1, tooltip: str | None = None):
  return html.Div(id=f"{id_}-container", children=[
    html.Span(f"{id_.replace('-', ' ')}"),
    html.Div(id=f"{id_}-tooltip-icon-wrapper", className="tooltip-icon-wrapper", children=[
      html.I(id=f"{id_}-tooltip-icon", className="fa-regular fa-circle-question fa-2xs") if tooltip else html.I()
    ]),
    dbc.Tooltip(id=f"{id_}-tooltip", target=f"{id_}-tooltip-icon-wrapper", placement="bottom", children=tooltip),
    html.Div(id=f"{id_}-filter", className="mix-max-filter", children=[
      dbc.Input(
        id={"type": "erank-filter", "id": f"min-{id_}"},
        type="number",
        min=min_,
        step=step,
        size="sm",
        placeholder="min"
      ),
      dbc.Input(
        id={"type": "erank-filter", "id": f"max-{id_}"},
        type="number",
        min=min_,
        step=step,
        size="sm",
        placeholder="max"
      )
    ])
  ])

def get_input_filter(id_, tooltip: str | None = None):
  return html.Div(id=f"{id_}-container", children=[
    html.Span(f"{id_.replace('-', ' ')}"),
    html.Div(id=f"{id_}-tooltip-icon-wrapper", className="tooltip-icon-wrapper", children=[
      html.I(id=f"{id_}-tooltip-icon", className="fa-regular fa-circle-question fa-2xs") if tooltip else html.I()
    ]),
    dbc.Tooltip(id=f"{id_}-tooltip", target=f"{id_}-tooltip-icon-wrapper", placement="bottom", children=tooltip),
    html.Div(id=f"{id_}-filter", className="input-filter", children=[
      dbc.Input(
        id={"type": "erank-filter", "id": id_},
        type="text",
        size="sm",
      )
    ])
  ])

def get_checklist_filter(id_, options: list[tuple[str, Any]], inline = False, tooltip: str | None = None):
  return html.Div(id=f"{id_}-container", children=[
    html.Span(f"{id_.replace('-', ' ')}"),
    html.Div(id=f"{id_}-tooltip-icon-wrapper", className="tooltip-icon-wrapper", children=[
      html.I(id=f"{id_}-tooltip-icon", className="fa-regular fa-circle-question fa-2xs") if tooltip else html.I()
    ]),
    dbc.Tooltip(id=f"{id_}-tooltip", target=f"{id_}-tooltip-icon-wrapper", placement="bottom", children=tooltip),
    html.Div(id=f"{id_}-filter", className="checklist-filter", children=[
      dbc.Checklist(
        id={"type": "erank-filter", "id": id_},
        options=[{"label": option[0], "value": option[1]} for option in options],
        value=[option[1] for option in options],
        inline=inline
      ),
    ])
  ])

min_max_filters = [
  get_min_max_filter(id_, min_, step_, tooltip)
  for id_, min_, step_, tooltip in zip(
    ("word-count", "etsy-competition", "google-searches", "google-cpc", "average-searches", "average-clicks", "average-ctr", "average-csi", "tag-occurrences"),
    (0, 0, 0, 0, 0, 0, 0, 0, 0),
    (1, 1, 1, 1, 1, 1, 1, 1, 1),
    (None, None, None, "(Cost-Per-Click) indicates how much advertisers are prepared to pay for the keyword", None, None, "(Click-Through Rate) The ratio of clicks to searches", "(Competition/Search Index) A measurement for effectiveness of a keyword based on it's search volume, ctr and competition, the lower the better", None)
  )
]
input_filters = [
  get_input_filter(id_, tooltip)
  for id_, tooltip in zip(
    ("include-keywords", "exclude-keywords"),
    (None, None)
  )
]
checklist_filters = [
  get_checklist_filter(id_, options, inline, tooltip)
  for id_, options, inline, tooltip in zip(
    ("long-tail-keyword", ),
    ([("Yes", "Yes"), ("No", "No"), ("Maybe", "Maybe")], ),
    (True, ),
    ("A vague indication of if a keyword or a key phrase is more specific than generic", )
  )
]

all_filters = min_max_filters + input_filters + checklist_filters

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
        dcc.Store(id="erank-crawler-session-id", storage_type="local")
      ])
    ]),
    html.Div(id="erank-filter-container", children=[
      html.Div(id="erank-filters", children=all_filters),
      dcc.Store("erank-filter-query", data=ErankFilterQuery().dict())
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
          for col_name in ("keywords", "tag occurrences", "average searches", "average clicks", "average ctr", "average csi", "etsy competition", "google searches", "google cpc", "long tail keyword")
        ]),
        dcc.Loading(id="erank-data-container")
      ]),
      html.Div(id="erank-data-container-removed", children=[
        
      ]),
    ])
  ])
])
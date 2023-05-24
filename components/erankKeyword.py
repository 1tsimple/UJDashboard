import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Any

def get_keyword_data_container(
  keyword: str,
  tag_occurrences: int,
  average_searches: int,
  average_clicks: int,
  average_ctr: float,
  average_csi: float,
  etsy_competition: int,
  google_searches: int,
  google_cpc: float,
  long_tail_keyword: str
):
  return dbc.Alert(
    id={"type": "erank-keyword-data-card", "id": keyword},
    className="erank-keyword-data-card",
    children=[
      html.Div(className="erank-keyword-wrapper", children=html.Span(keyword)),
      html.Div(className="erank-tag-occurrences-wrapper", children=html.Span(tag_occurrences)),
      html.Div(className="erank-average-searches-wrapper", children=html.Span(average_searches)),
      html.Div(className="erank-average-clicks-wrapper", children=html.Span(average_clicks)),
      html.Div(className="erank-average-ctr-wrapper", children=html.Span(round(average_ctr, 2) if average_ctr else None)),
      html.Div(className="erank-average-csi-wrapper", children=html.Span(round(average_csi, 2) if average_csi else None)),
      html.Div(className="erank-etsy-competition-wrapper", children=html.Span(etsy_competition)),
      html.Div(className="erank-google-searches-wrapper", children=html.Span(google_searches)),
      html.Div(className="erank-google-cpc-wrapper", children=html.Span(google_cpc)),
      html.Div(className="erank-long-tail-keyword-wrapper", children=html.Span(long_tail_keyword)),
      html.Button(id={"type": "erank-keyword-data-card-close-button", "id": keyword}, type="button", className="fa-regular fa-square-minus erank-keyword-data-card-close-button")
    ]
  )
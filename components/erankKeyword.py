import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def get_keyword_data_container(
  keyword: str,
  character_count: str,
  tag_occurrences: str,
  average_searches: str,
  average_clicks: str,
  average_ctr: str,
  etsy_competition: str,
  google_searches: str,
  google_cpc: str,
  google_competition: str,
  long_tail_keyword: str
):
  return dbc.Alert(
    id={"type": "erank-keyword-data-container", "id": keyword},
    children=[
      html.Div(className="erank-keyword-wrapper", children=html.Span(keyword)),
      html.Div(className="erank-character-count-wrapper", children=html.Span(character_count)),
      html.Div(className="erank-tag-occurrences-wrapper", children=html.Span(tag_occurrences)),
      html.Div(className="erank-average-searches-wrapper", children=html.Span(average_searches)),
      html.Div(className="erank-average-clicks-wrapper", children=html.Span(average_clicks)),
      html.Div(className="erank-average-ctr-wrapper", children=html.Span(average_ctr)),
      html.Div(className="erank-etsy-competition-wrapper", children=html.Span(etsy_competition)),
      html.Div(className="erank-google-searches-wrapper", children=html.Span(google_searches)),
      html.Div(className="erank-google-cpc-wrapper", children=html.Span(google_cpc)),
      html.Div(className="erank-google-competition-wrapper", children=html.Span(google_competition)),
      html.Div(className="erank-long-tail-keyword-wrapper", children=html.Span(long_tail_keyword)),
      html.Button(id={"type": "erank-keyword-data-container", "id": keyword}, type="button", className="btn-close")
    ]
  )
import dash
from dash import html, dcc

def get_header():
  return html.Div(id="header-inner", children=[
    html.Div(id="logo-container", children=[
      
    ]),
    html.Nav(id="navbar", children=[
      html.Ul(children=[
        html.Li(id=page["name"], children=dcc.Link(href=page["path"], children=html.Span(children=page["name"])))
        for page in dash.page_registry.values()
      ])
    ])
  ])
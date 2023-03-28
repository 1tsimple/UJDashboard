import dash
from dash import html, dcc

def get_header():
  pages = dash.page_registry
  return html.Div(id="header-inner", children=[
    html.Div(id="logo-container", children=[
      html.H1(id="logo", children="UJ")
    ]),
    html.Nav(id="navbar", children=[
      html.Ul(children=[
        html.Li(id=pages["pages.home"]["name"], children=dcc.Link(
          href=pages["pages.home"]["path"], children=[
            html.Span(children=pages["pages.home"]["name"]),
            html.I(id="home-icon", className="fa-solid fa-house")
          ]
        )),
        html.Li(id=pages["pages.database"]["name"], children=dcc.Link(
          href=pages["pages.database"]["path"], children=[
            html.Span(children=pages["pages.database"]["name"]),
            html.I(id="database-icon", className="fa-solid fa-database")
          ]
        )),
        html.Li(id=pages["pages.log"]["name"], children=dcc.Link(
          href=pages["pages.log"]["path"], children=[
            html.Span(children=pages["pages.log"]["name"]),
            html.I(id="log-icon", className="fa-solid fa-file-lines")
          ]
        ))
      ])
    ])
  ])
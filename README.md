# demo_dash

Creating different dashboards for visualizations of the stock and crypto markets
- Try different trading stratagies 
- correlations between different sets of stocks
- correlations between news and stocks
- correlations between tweets by and stocks

# Goldman Sachs
Taking some data and trading strategies form GoldmanSach's open source project

https://developer.gs.com/docs/gsquant/tutorials/

https://github.com/goldmansachs/gs-quant

# Alpaca
Using Alpaca to test out trading algorithems
https://alpaca.markets/

# Blogs
yfinance blog 
- https://aroussi.com/post/python-yahoo-finance
- https://github.com/ranaroussi/yfinance

# Getting started with environment variables
- https://pypi.org/project/python-dotenv/

# finnhub
Documentations 
finnhub : https://finnhub.io/docs/api#news-sentiment
new and stock information

# Creating Dashboards with dash
https://dash.plotly.com/
simple template is 
```
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
```
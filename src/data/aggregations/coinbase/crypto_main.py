import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import constants as const
import pandas as pd
import aggregate_crypto as wallet
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = wallet.get_transactions(const.IGNORE)[1]
app.layout = html.Div([
    dcc.Graph(id='crypto_holding'),
    dcc.Checklist(
        id='coin_checklist',
        options=[
            {'label': 'BTC', 'value': 'BTC'},
            {'label': 'ETH', 'value': 'ETH'},
            {'label': 'XRP', 'value': 'XRP'}
        ],
        value=['BTC'],
        labelStyle={'display': 'inline-block'}
    )  
])


@app.callback(
    Output('crypto_holding', 'figure'),
    [Input('coin_checklist', 'value')])
def update_figure(name):

    fig = px.scatter(df, x=const.CHANGED_AMOUNT_DIFFERENCE_USD, y=const.CHANGED_AMOUNT_DIFFERENCE_PERCENT, 
                     size=const.VALUE, color="name",
                     size_max=55)

    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
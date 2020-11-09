
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go # or plotly.express as px
import os
from dotenv import load_dotenv
from data.aggregations.alapca import test_algo
from data.aggregations.alapca import data as alpaca_data
import pandas as pd

'''
load_dotenv()
acc = alpaca_data.alpaca_account()
results = acc.get_bar('15Min', 'AAPL', '2020-10-25', '2020-11-1')
'''

'''
Plotly autoscale Y axis : 
yaxis=dict(
       autorange = True,
       fixedrange= False
   )
'''

import plotly.graph_objects as go

import pandas as pd
from datetime import datetime


# df = pd.read_csv('Results.csv')

# print(df[('AAPL', "open")])
# fig = go.Figure(data=[go.Candlestick(x=df["Date"],
#                 open=df['AAPL.open'],
#                 high=df['AAPL.high'],
#                 low=df['AAPL.low'],
#                 close=df['AAPL.close'])])

# fig.show()

if __name__ == "__main__":
    # Obtain the Data
    # result = pd.read_csv('Results.csv')
    load_dotenv()
    acc = alpaca_data.alpaca_account()
    results = acc.get_bar('15Min', 'AAPL', '2020-10-1', '2020-11-1')
    print("----")
    # print(results.columns)
    # print(results['AAPL','open'])
    # print(results['AAPL'])
    appl = results['AAPL'].reset_index().rename(columns={'index':'date'})
    appl = appl.reset_index()
    print(appl)
    fig = go.Figure(data=[go.Candlestick(
                x=appl["date"],
                open=appl['open'],
                high=appl['high'],
                low=appl['low'],
                close=appl['close'])],
                layout= {
                    'height': 1200, 
                    'width': 1800,
                    'xaxis' : {
                        'type' : 'category',
                        'categoryorder' : 'category ascending',
                        },

                    },
                )

    app = dash.Dash()
    
    app.layout = html.Div([
            dcc.Graph(
                id="my-graph",
                figure=fig,
                
                ),
            ]
        )
    # updates teh X axis
    # fig.update_xaxes(
    # ticktext=["End of Q1", "End of Q2", "End of Q3", "End of Q4"],
    # tickvals=["2016-04-01", "2016-07-01", "2016-10-01", apple_df_2016.index.max()],
    # )
    app.run_server(debug=True, use_reloader=False) 
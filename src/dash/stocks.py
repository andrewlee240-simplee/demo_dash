
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go # or plotly.express as px
import pandas as pd

'''
Creating a candlestick 
df : dataframe
values : a dictionary holding the column names
'''
def candlestick(df, values):

    # Lets keep the variable decleration cleaner by defining here
    x_value = df[values['date']]
    open_value = df[values['open']]
    high_value = df[values['high']]
    low_value = df[values['low']]
    close_value = df[values['close']]
    
    fig = go.Figure(data=[go.Candlestick(
                x= x_value,
                open= open_value,
                high= high_value,
                low= low_value,
                close= close_value,
                )
            ],
    # The layout uses dates as a categorical value, 
    # removing spaces where markets weren't open
            layout= {
                'xaxis' : {
                    'type' : 'category',
                    'categoryorder' : 'category ascending',
                    },
                },
            )
    
    return fig

import dash
import os
from dotenv import load_dotenv
from data.aggregations.alapca import test_algo

# load and create connections to apis
def connect_and_load():
    load_dotenv()

    # connecting to Alpaca

def create_dash():
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


if __name__ == "__main__":
    # Load api keys
    load_dotenv()

    print(os.getenv('FINNHUB'))
    print(os.getenv('ALPACA'))
    pass
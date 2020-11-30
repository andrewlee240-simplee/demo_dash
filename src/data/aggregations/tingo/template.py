import pandas as pd
from dotenv import load_dotenv
from os import name, path
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os

load_dotenv()
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Need to account for transfers to a different crypto
def example_template():
    url = "https://api.tiingo.com/tiingo/crypto/prices"
    session = Session()
    parameters = {
        'token' : os.getenv('TIINGO_API_KEY'),
        'tickers' : 'btcusd',
        'startDate' : '2018-01-01',
        'resampleFreq' : '1day'
    }

    headers = {
        'Content-Type': 'application/json'
    }

    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        with open('data/historical/bitcoin_data_day.json', 'w') as outfile:
            json.dump(data, outfile)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def historical_values(ticker, startDate, freq):
    url = "https://api.tiingo.com/tiingo/crypto/prices"
    session = Session()
    parameters = {
        'token' : os.getenv('TIINGO_API_KEY'),
        'tickers' : ticker,
        'startDate' : startDate,
        'resampleFreq' : freq
    }

    headers = {
        'Content-Type': 'application/json'
    }

    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        return data
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
    return 

results = historical_values('ethusd', '2018-01-01','1day')
print(results)
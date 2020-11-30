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
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start':'1',
        'limit':'5000',
        'convert':'USD'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.getenv('COIN_MARKETCAP_API_KEY'),
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)




if __name__ == "__main__":
    example_template()
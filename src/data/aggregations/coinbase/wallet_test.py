from coinbase.wallet.client import Client
import pandas as pd
import os
from datetime import datetime
import copy
import numpy as np
import logging
from dotenv import load_dotenv
import sys

# import two file that contain our coin and wallet object
from coin import coin
from wallet import wallet

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
COINBASE_KEY = 'COINBASE_KEY_V2'
COINBASE_SECRET = 'COINBASE_SECRET_V2'

const = (COINBASE_KEY , COINBASE_SECRET)

# Create our wallet
load_dotenv()

def get_portfolio():
    # Getting our api key
    api_key = os.getenv(COINBASE_KEY)
    api_secret = os.getenv(COINBASE_SECRET)

    # set up our wallet
    my_wallet = wallet(api_key, api_secret)
    if my_wallet is not None:
        my_wallet.filter_dates('2000-01-01')
        # my_wallet.coin_filter(['REN', 'ETH' , 'BTC'])
        my_wallet.get_costbasis()
        summary = pd.DataFrame(my_wallet.coin_profits)
        print(summary.sort_values(by=['Current Value'], ascending=False))
        print('Total Return : {}'.format(summary['Current Value'].sum() - summary['usd_balance'].sum()))
        print('Total Input USD : {}'.format(summary['usd_balance'].sum()))
        print('Total Value : {}'.format(summary['Current Value'].sum()))
        print('Total Return : {}'.format(summary['Diff Value'].sum()))
        summary.to_csv('summary_file.csv')

get_portfolio()
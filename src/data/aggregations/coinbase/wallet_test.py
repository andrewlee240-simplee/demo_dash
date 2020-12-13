from coinbase.wallet.client import Client
import pandas as pd
import os
from datetime import datetime
import copy
import numpy as np
import logging
from dotenv import load_dotenv

# import two file that contain our coin and wallet object
from coin import coin
from wallet import wallet

COINBASE_KEY = 'COINBASE_KEY'
COINBASE_SECRET = 'COINBASE_SECRET'

const = (COINBASE_KEY , COINBASE_SECRET)

# Create our wallet
load_dotenv()

def get_portfolio():
    # Getting our api key
    api_key = os.getenv(COINBASE_KEY)
    api_secret = os.getenv(COINBASE_SECRET)

    # set up our wallet
    my_wallet = wallet(api_key, api_secret)
    my_wallet.get_costbasis()
get_portfolio()
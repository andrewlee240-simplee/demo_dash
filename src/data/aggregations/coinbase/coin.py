from coinbase.wallet.client import Client
import pandas as pd
import os
from datetime import datetime
import copy
import numpy as np
import logging

'''
Loading Variables for testing.
'''
from dotenv import load_dotenv
load_dotenv()
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

NAME = 'name'
AMOUNT = 'amount'
AMOUNT_CHANGED = 'amount_changed'
USD = 'usd'
RATE = 'rate'
DATE_CREATED = 'date_created'
CURRENT_VALUE = 'current_value'
PURCHASED_VALUE = 'purchased_value'
SOLD_VALUE = 'sold_value'
CURRENT_COIN_BALANCE = 'current_coin_balance'
PREVIOUS_COIN_BALANCE = 'previous_coin_balance'

constants = (NAME, AMOUNT, AMOUNT_CHANGED, USD, RATE , DATE_CREATED, CURRENT_VALUE, PURCHASED_VALUE, SOLD_VALUE, CURRENT_COIN_BALANCE, PREVIOUS_COIN_BALANCE)


# Class that represents our holdings of a coin.

class coin():
    def __init__(self, name, transactions, client):
        self.name = name
        self.transctions = transactions
        self.client = client


from coinbase.wallet.model import Account
from dotenv import load_dotenv
import os
from coinbase.wallet.client import Client
import datetime
import pandas as pd
import logging
from datetime import datetime, date
import crypto_class as cc # import class crypto as variable cc

pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

load_dotenv()

# Before implementation, set environmental variables with the names API_KEY and API_SECRET

API_KEY = os.getenv('COINBASE_KEY')
API_SECRET = os.getenv('COINBASE_SECRET')

client = Client(API_KEY, API_SECRET)
accounts = client.get_accounts()

def get_transactions(ignore=None):
    cryptos = {}
    if ignore is None:
        ignore = []
    for account in accounts['data']:
        if account['id'] != account['currency'] and account['currency'] not in ignore:
            transactions = client.get_transactions(account['id'])
            cyrpto_trans = []
            for transaction in transactions['data']:
                cyrpto_trans.append({
                    'type' : transaction['type'],
                    'created_at' : transaction['created_at'],
                    'balance' : dict(transaction['amount']),
                    'native_balance' : dict(transaction['native_amount']),
                    'full_transaction' : transaction,
                    'type' : transaction['type']
                })
            cryptos[account['currency']] = {
                'transactions' :  cyrpto_trans
            }

    # Aggregate Transactions
    # return a dictionary of crypto classes after running some data cleans
    crypto_class = {}
    for x in cryptos:
        # Create different classes for each crypto type
        crypto_class[x] = cc.crypto(x , cryptos[x], client)
        crypto_class[x].set_balance()
        crypto_class[x].get_balance()
        crypto_class[x].parse_transactions()
        # crypto_class[x].print_balances()
        print(crypto_class[x].name)
    wallet = cc.wallet(crypto_class)
    wallet.aggregate_coins()

IGNORE = ['USD']
get_transactions(IGNORE)
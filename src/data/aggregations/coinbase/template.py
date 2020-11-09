from coinbase.wallet.model import Account
from dotenv import load_dotenv
import os
from coinbase.wallet.client import Client
import datetime
import pandas as pd

load_dotenv()
# Before implementation, set environmental variables with the names API_KEY and API_SECRET
# API_KEY = os.getenv('COINBASE_KEY_V2')
# API_SECRET = os.getenv('COINBASE_SECRET_V2')

API_KEY = os.getenv('COINBASE_KEY')
API_SECRET = os.getenv('COINBASE_SECRET')

client = Client(API_KEY, API_SECRET)
accounts = client.get_accounts()

# Get Crypto Transactions
def aggregate_transactions():
    cryptos = {}

    for account in accounts['data']:
        if account['id'] != account['currency']:
            transactions = client.get_transactions(account['id'])
            cyrpto_trans = []
            for transaction in transactions['data']:
                cyrpto_trans.append({
                    'type' : transaction['type'],
                    'created_at' : transaction['created_at'],
                    'balance' : dict(transaction['amount']),
                    'native_balance' : dict(transaction['native_amount']),
                })
            cryptos[account['currency']] = {
                'transactions' :  cyrpto_trans
            }

    # Aggregate Transactions

    balance = {}
    for crypto in cryptos:
        # Usd dollars that went in and the total amount of crypto that we bought
        usd_balance = 0
        crypt_balance = 0

        for transaction in cryptos[crypto]['transactions']:
            # print(transaction)
            usd_balance += float(transaction['native_balance']['amount'])
            crypt_balance += float(transaction['balance']['amount'])

        price_usd = client.get_spot_price(currency_pair = str(crypto) + '-USD')
        total_balance = crypt_balance * float(price_usd['amount'])

        cryptos[crypto]['balances'] = {
                                        'usd_balance' : usd_balance,
                                        'net_return' : total_balance - usd_balance,
                                        'total_balance' : total_balance
                                    }
        

        # print("\t current amount$" , data[crypto]['native_balance'])

    net_return = 0
    total_balance = 0
    for crypto in cryptos:
        print(crypto)
        print("\tNet Return $", cryptos[crypto]['balances']['net_return'])
        net_return += cryptos[crypto]['balances']['net_return']
        total_balance += cryptos[crypto]['balances']['total_balance']

    results = {
        'total_return' : net_return,
        'total_balance' : total_balance,
        'data' : cryptos
    }
    print("Total Return" , net_return)
    print("Total Balance" , total_balance)
    print(results['data'])
    df = pd.DataFrame(results['data'])
    print(df)
    return results


aggregate_transactions()

# txs = client.get_transactions('2bbf394c-193b-5b2a-9155-3b4732659ede')
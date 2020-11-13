from coinbase.wallet.model import Account
from dotenv import load_dotenv
import os
from coinbase.wallet.client import Client
import datetime
import pandas as pd
import logging
from datetime import datetime, date
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

load_dotenv()

# Before implementation, set environmental variables with the names API_KEY and API_SECRET

API_KEY = os.getenv('COINBASE_KEY')
API_SECRET = os.getenv('COINBASE_SECRET')

client = Client(API_KEY, API_SECRET)
accounts = client.get_accounts()

# Column Names for DataFrame
CN_DF = {
    'amount' : 'amount',
    'usd' : 'usd',
    'rate' : 'rate(cypto/usd)',
    'date' : 'date',
    'date_created' : 'created_at',
    'total_value' : 'total_value',
    'total_coin' : 'total_coin',
    'net_change' : 'net_change'
}

# We should define a class for each CryptoCurrency
# After defining the class we should create a transaction dataframe
# Once we have a clean spreadsheet we can see how each transaciton affects our netvalue

def aggregate_transactions(ignore=None):
    # Get Crypto Transactions
    cryptos = {}
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
                })
            cryptos[account['currency']] = {
                'transactions' :  cyrpto_trans
            }

    # Aggregate Transactions
    for crypto in cryptos:
        # Usd dollars that went in and the total amount of crypto that we bought
        usd_balance = 0
        crypt_balance = 0

        for transaction in cryptos[crypto]['transactions']:
            usd_balance += float(transaction['native_balance']['amount'])
            crypt_balance += float(transaction['balance']['amount'])

        price_usd = client.get_spot_price(currency_pair = str(crypto) + '-USD')
        price_usd_amount = float(price_usd['amount'])
        total_balance = crypt_balance * price_usd_amount

        cryptos[crypto]['balances'] = {
                                        'usd_balance' : usd_balance,
                                        'net_return' : total_balance - usd_balance,
                                        'total_balance' : total_balance,
                                        'crypto_price' : price_usd_amount,
                                        'crypt_balance' : crypt_balance
                                    }
        

        # print("\t current amount$" , data[crypto]['native_balance'])

    net_return = 0
    total_balance = 0
    crypto_balance = {}

    for crypto in cryptos:
        print(crypto)
        print("\tNet Return $", cryptos[crypto]['balances']['net_return'])
        net_return += cryptos[crypto]['balances']['net_return']
        total_balance += cryptos[crypto]['balances']['total_balance']
        crypto_balance[crypto] = {
            'total_balance' : cryptos[crypto]['balances']['total_balance'],
            'net_return' : cryptos[crypto]['balances']['net_return'],
            'dollar_amount' : cryptos[crypto]['balances']['crypto_price'] * (cryptos[crypto]['balances']['total_balance']),
            'crypto_price' : cryptos[crypto]['balances']['crypto_price'],
        }
    results = {
        'total_return' : net_return,
        'total_balance' : total_balance,
        'data' : cryptos
    }

    crypto_value = {}
    for crypto in results['data']:

        crypto_value[(crypto , CN_DF['amount'])] = []
        crypto_value[(crypto , CN_DF['usd'])] = []
        crypto_value[(crypto , CN_DF['rate'])] = []
        crypto_value[(crypto , CN_DF['total_value'])] = []
        crypto_value[(crypto , CN_DF['total_coin'])] = []
        crypto_value[(crypto , CN_DF['net_change'])] = []
        crypto_value[(crypto , CN_DF['date_created'])] = []
        total_value = results['data'][crypto]['balances']['total_balance'] 
        total_coin = results['data'][crypto]['balances']['crypt_balance']
        total_spent = results['data'][crypto]['balances']['total_balance']
        # print(results['data'][crypto]['balances']['total_balance'])
        for trans in results['data'][crypto]['transactions']:
            
            # Date Control Filter
            # if 
            total_spent = (results['data'][crypto]['balances']['crypto_price'] - float(trans['native_balance']['amount']) / float(trans['balance']['amount'])) / results['data'][crypto]['balances']['crypto_price'] * 100
            crypto_value[(crypto , CN_DF['amount'])].append(trans['balance']['amount'])
            crypto_value[(crypto , CN_DF['usd'])].append(trans['native_balance']['amount'])
            crypto_value[(crypto , CN_DF['rate'])].append(float(trans['native_balance']['amount']) / float(trans['balance']['amount']))
            crypto_value[(crypto , CN_DF['date_created'])].append(datetime.strptime(trans[CN_DF['date_created']], '%Y-%m-%dT%XZ'))
            crypto_value[(crypto , CN_DF['total_value'])].append(total_value)
            crypto_value[(crypto , CN_DF['total_coin'])].append(total_coin)
            crypto_value[(crypto , CN_DF['net_change'])].append(total_spent)
            total_coin -= float(trans['balance']['amount'])
            total_value = total_coin * (float(trans['native_balance']['amount']) / float(trans['balance']['amount']))
            # crypto_value[(x , 'rate')].append(float(trans['balance']['amount']) / float(trans['native_balance']['amount']))
        
    df = pd.DataFrame.from_dict(crypto_value, orient='index')
    
    df = df.transpose()
    crypto_index = (crypto_value.keys())
    index = pd.MultiIndex.from_tuples(crypto_index)

    df = pd.DataFrame(df, columns=index)

    # print(df['total_coin'])
    # print(df[['amount']])
    print(df.index)
    print(df.columns)
    # print(df.xs('created_at', axis=1, level=1, drop_level=False))
    filter = df.xs('created_at', axis=1, level=1, drop_level=False)

    # print(df.loc[datetime.date(year=2020,month=1,day=1):datetime.now()])
    print(filter)
    for x in crypto_balance:
        print(x , crypto_balance[x])
    
    print("Total Return" , net_return)
    print("Total Balance" , total_balance)

    return results

IGNORE = ['USD']
aggregate_transactions(IGNORE)

# txs = client.get_transactions('2bbf394c-193b-5b2a-9155-3b4732659ede')
from coinbase.wallet.client import Client
import pandas as pd
import os
from datetime import datetime
import copy

# Define Constants for consitency of dictionarys and dataframes
RATE = 'rate'
AMOUNT_CHANGED = 'amount_changed_coin'
USD = 'usd'
DATE_CREATED = 'date_created'
TOTAL_VALUE = 'total_value_dollar'
COIN_BALANCE = 'coin_balance'
NET_CHANGE = 'net_change_dollar'
DATE = 'date'
COIN_BALANCE = 'coin_balance'
NET_CHANGE = 'net_change_percent'
NAME = 'name'
BALANCE_CHANGE = 'balance_change_now_usd'
NATIVE_BALANCE = 'native_balance'
TRANSACTION_AMOUNT = 'amount'
CRYPTO_BALANCE = 'balance'
ACCUMULATED_COINS = 'accumulated_coins'
ACCUMULATED_USD = 'accumulated_usd_value'
ACCOUNT_ACCUMULATED_USD = 'cummulative_account_usd'
ACTUAL_PROFIT = 'actual_profit'
TOTAL_VALUE_USD_AT_TIME = 'total_value_usd_at_time'


class crypto():
    def __init__(self, name, info, client):
        
        self.name = name
        self.info = info
        self.client = client
        # Creating Placeholder Variables
        self.current_value = None
        self.coin_balance = None
        self.current_exchange = None
        self.transactions = None    
        self.net_return = None
        self.usd_balance = None
        self.percent_return = None
        self.balances = None
        self.current_rate = None
        # Column name match with value used in transaction dictionary
        self.column_names = {
            AMOUNT_CHANGED : 'amount_changed',
            USD : 'usd',
            RATE : 'rate(cypto/usd)',
            DATE_CREATED : 'created_at',
            TOTAL_VALUE : 'total_value',
            COIN_BALANCE : 'coin_balance',
            NET_CHANGE : 'net_change',
            NAME : 'name',
            BALANCE_CHANGE : 'balance_change',
        }

            # ACCUMULATED_USD : 'accumulated_usd',
            # ACCUMULATED_COINS : 'accumulated_coins',
            # ACCOUNT_ACCUMULATED_USD : 'cummulative_account_usd',
            # ACTUAL_PROFIT : 'actual_profit'
    # def transaction_df(self):

    def set_balance(self):
        usd_balance = 0
        crypt_balance = 0

        transactions = self.info['transactions']
        for transaction in transactions:
            usd_balance += float(transaction[NATIVE_BALANCE][TRANSACTION_AMOUNT])
            crypt_balance += float(transaction[CRYPTO_BALANCE][TRANSACTION_AMOUNT])

        price_usd = (self.client).get_spot_price(currency_pair = (self.name + '-USD'))
        price_usd_amount = float(price_usd[TRANSACTION_AMOUNT])
        total_balance = crypt_balance * price_usd_amount


        self.usd_balance = usd_balance
        self.net_return = total_balance - usd_balance
        self.current_exchange = price_usd_amount
        self.coin_balance = crypt_balance
        self.percent_return = round(self.net_return / self.usd_balance , 6) * 100 
        self.current_rate = price_usd_amount

    def parse_transactions(self):
        crypto_dict = {}
        # Iterate defined column names and intialize empty list that we add to, then convert to a dataframe
        for x in self.column_names:
            crypto_dict[x] = []

        usd_balance = self.usd_balance 
        coin_balance = self.coin_balance
        net_change = self.usd_balance 

        # We want to add a column to see what our current values are now...
        # So we add an empty trnasaction


        for trans in self.info['transactions']:
            # (Diff value from purchase and current value)
            usd_amount = float(trans[NATIVE_BALANCE][TRANSACTION_AMOUNT])
            crypto_amount = float(trans[CRYPTO_BALANCE][TRANSACTION_AMOUNT])

            # Get the difference in current rate vs the ratio between the amount usd spent and crypto accumulated
            net_change = (self.current_rate - usd_amount / crypto_amount) / self.current_rate * 100

            crypto_dict[AMOUNT_CHANGED].append(crypto_amount)
            crypto_dict[USD].append(usd_amount)
            crypto_dict[RATE].append(usd_amount / crypto_amount)
            crypto_dict[DATE_CREATED].append(datetime.strptime(trans[self.column_names[DATE_CREATED]], '%Y-%m-%dT%XZ').date())
            
            # Round Values
            usd_balance = round(usd_balance, 6)
            coin_balance = round(coin_balance, 6)
            crypto_amount = round(crypto_amount, 6)

            # Value in USD, calculated on current rate * total balance
            crypto_dict[TOTAL_VALUE].append(usd_balance)

            # Total Number of Coins
            crypto_dict[COIN_BALANCE].append(coin_balance)

            # Percent value changed of Crypto from day of purchase
            crypto_dict[NET_CHANGE].append(net_change)
            crypto_dict[NAME].append(self.name)

            # difference in balance compared to today
            crypto_dict[BALANCE_CHANGE].append(round(usd_balance * net_change / 100 , 6))
            coin_balance -= crypto_amount
            usd_balance = coin_balance * (usd_amount / crypto_amount)
        
        # for x in crypto_dict:
        #     print(x , crypto_dict[x])
        # return

        df = pd.DataFrame.from_dict(crypto_dict)

        # getting current rate
        current_price = round(float(self.client.get_spot_price(currency_pair = (self.name + '-USD'))['amount']),6)
        net_change_now = (self.current_rate - self.usd_balance / self.coin_balance) / self.current_rate * 100
        empty_transaction = {
            AMOUNT_CHANGED : [0],
            USD : [0],
            RATE : [current_price],
            DATE_CREATED : [datetime.now().strftime('%Y-%m-%d')],
            TOTAL_VALUE : [self.usd_balance],
            COIN_BALANCE : [self.coin_balance],
            NET_CHANGE : [net_change_now],
            NAME : [self.name],
            BALANCE_CHANGE : [usd_balance * net_change / 100] ,
        }

        # results = pd.DataFrame.from_dict(empty_transaction)

        df = pd.concat([pd.DataFrame.from_dict(empty_transaction), df], ignore_index=True)

        df[TOTAL_VALUE_USD_AT_TIME] = df[COIN_BALANCE] * df[RATE]

        # I want to get the difference in values 

        df[ACCOUNT_ACCUMULATED_USD] = df.loc[::-1, 'usd'].cumsum()[::-1]
        df[ACTUAL_PROFIT] =  round(df[TOTAL_VALUE_USD_AT_TIME] - df[ACCOUNT_ACCUMULATED_USD], 2)
        df[ACCUMULATED_COINS] = round(df.loc[::-1, AMOUNT_CHANGED].cumsum()[::-1], 4)
        df[ACCUMULATED_USD] = round(df[ACCUMULATED_COINS] * df[RATE], 4)
        # Create value at time
        value = df['usd'].sum()
        

        print(df)
        print(value)
        print(self.usd_balance)
        print(self.balances['net_return'])
        
    def get_balance(self):
        balance = {
            'usd_balance' : self.usd_balance,
            'net_return' : self.net_return,
            'rate' : self.current_exchange,
            'coin_balance' : self.coin_balance,
            'percent_return' : self.percent_return 
        }
        self.balances = balance
        return balance

    def print_balances(self):
        print(self.name)
        for x in self.balances:
            print('\t' , x, '\t' , self.balances[x])
        # for x in self.info['transactions']:
        #     print(x)
        #     print("----")


class crypto_wallet():
    def __init__(self):
        self.net = 0

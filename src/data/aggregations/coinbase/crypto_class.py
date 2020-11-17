from coinbase.wallet.client import Client
import pandas as pd
import os
from datetime import datetime
import copy
import numpy as np
from constants import ( RATE, AMOUNT_CHANGED, USD, DATE_CREATED , 
                        TOTAL_VALUE, COIN_BALANCE, NET_CHANGE,
                        NAME, BALANCE_CHANGE, NATIVE_BALANCE, 
                        TRANSACTION_AMOUNT, CRYPTO_BALANCE, ACCUMULATED_COINS, 
                        ACCUMULATED_USD, ACCOUNT_ACCUMULATED_USD, ACTUAL_PROFIT, 
                        TOTAL_VALUE_USD_AT_TIME, AMOUNT_CHANGED_VALUE_NOW, 
                        CHANGED_AMOUNT_DIFFERENCE_PERCENT, 
                        CHANGED_AMOUNT_DIFFERENCE_USD,VALUE, IGNORE)


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
        self.df = None
        # Column name match with value used in transaction dictionary
        self.column_names = {
            NAME : 'name',
            AMOUNT_CHANGED : 'amount_changed',
            USD : 'usd',
            RATE : 'rate(cypto/usd)',
            DATE_CREATED : 'created_at',
            TOTAL_VALUE : 'total_value',
            COIN_BALANCE : 'coin_balance',
            NET_CHANGE : 'net_change',
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
        self.spot_rate = round(float(self.client.get_spot_price(currency_pair = (self.name + '-USD'))['amount']),6)

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
            net_change = self.current_rate / (usd_amount / crypto_amount) * 100 - 100

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
            crypto_dict[BALANCE_CHANGE].append(round(usd_balance * net_change / 100 , 2))
            coin_balance -= crypto_amount
            usd_balance = coin_balance * (usd_amount / crypto_amount)


        df = pd.DataFrame.from_dict(crypto_dict)

        # getting current rate
        # Purchased Rate
        current_price = float(self.client.get_spot_price(currency_pair = (self.name + '-USD'))['amount'])
        net_change_now = round(self.current_rate / (self.usd_balance  / self.coin_balance) * 100 - 100, 4)
        
        empty_transaction = {
            NAME : [self.name],
            TOTAL_VALUE : [self.usd_balance],
            COIN_BALANCE : [self.coin_balance],
            NET_CHANGE : [net_change_now],
            BALANCE_CHANGE : [round(usd_balance * net_change / 100, 2)] ,
            AMOUNT_CHANGED : [0],
            USD : [0],
            RATE : [current_price],
            DATE_CREATED : [datetime.now().strftime('%Y-%m-%d')],
        }

        # Add the empty transaction so that we can see our values with the current exchange rate
        df = pd.concat([pd.DataFrame.from_dict(empty_transaction), df], ignore_index=True)

        df[TOTAL_VALUE_USD_AT_TIME] = df[COIN_BALANCE] * df[RATE]
        df[AMOUNT_CHANGED_VALUE_NOW] = df[COIN_BALANCE] * current_price
        df[CHANGED_AMOUNT_DIFFERENCE_PERCENT] = df[AMOUNT_CHANGED_VALUE_NOW] / df[USD]
        df[CHANGED_AMOUNT_DIFFERENCE_PERCENT].replace(np.inf, 0, inplace=True)
        df[CHANGED_AMOUNT_DIFFERENCE_USD] = df[AMOUNT_CHANGED_VALUE_NOW] - df[USD]
        df[VALUE] = abs(df[USD])
        # I want to get the difference in values 

        # Reverse column values and get the cummulative sum then reverse that again and add to column
        # [::-1] will reverse the column values by iterative through it inversely

        df[ACCOUNT_ACCUMULATED_USD] = df.loc[::-1, USD].cumsum()[::-1] # Reverse column values and get the cummulative sum then reverse that again and add to column
        df[ACTUAL_PROFIT] =  round(df[TOTAL_VALUE_USD_AT_TIME] - df[ACCOUNT_ACCUMULATED_USD], 2)
        df[ACCUMULATED_COINS] = round(df.loc[::-1, AMOUNT_CHANGED].cumsum()[::-1], 4)

        # Accumulated USD calculated by coins * current rate
        df[ACCUMULATED_USD] = round(df[ACCUMULATED_COINS] * df[RATE], 4)

        self.df = df
        return df

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

    def aggregate(self):
        self.set_balance()
        self.parse_transactions()
        return self.df


class wallet():
    def __init__(self):
        self.profit = 0
        self.value = 0
        self.net_return = 0
        self.summary = {}
        self.holdings = []
        self.ignore = IGNORE

        api_key = os.getenv('COINBASE_KEY')
        api_secret = os.getenv('COINBASE_SECRET')
        self.client = Client(api_key, api_secret)
        self.accounts = self.client.get_accounts()

        self.coins = self.get_transactions()
        self.df = self.aggregate_coins()


    def get_transactions(self):
        cryptos = {}

        for account in self.accounts['data']:
            if account['id'] != account['currency'] and account['currency'] not in self.ignore:
                transactions = self.client.get_transactions(account['id'])
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

        # Aggregate TransactionsW
        # return a dictionary of crypto classes after running some data cleans
        crypto_class = {}
        for x in cryptos:
            # Create different classes for each crypto type
            crypto_class[x] = crypto(x , cryptos[x], self.client)
            crypto_class[x].set_balance()
            crypto_class[x].get_balance()
            crypto_class[x].parse_transactions()

        return crypto_class

# Implement a FIFO method to track profits of coins

    def aggregate_coins(self):
        df = pd.DataFrame()
        coins = self.coins
        for name in coins:
            coin = coins[name]
            coin.aggregate()
            temp_df = coin.df
            df = pd.concat([temp_df, df], ignore_index=True)
            self.holdings.append(name)
            self.summary[name] = coin.get_balance()
            self.profit += self.summary[name]['net_return']
            self.value += self.summary[name]['usd_balance']
        self.profit = round(self.profit, 2)
        return df
    
    def get_summary(self):
        for coin in self.summary:
            print('Coin' , coin)
            print('\tNet Return' , round(self.summary[coin]['net_return'], 4))
            print('\t% Return' , round(self.summary[coin]['percent_return'],4))
        print(round(self.profit, 4))
        print(round(self.profit / self.value, 4))
        # total
        # print(df)
# Implement a FIFO method to track profits of coins
    def get_costbasis(self):
        df = self.df
        print(df)
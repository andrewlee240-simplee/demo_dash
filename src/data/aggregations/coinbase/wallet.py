from coinbase.wallet.client import Client
import pandas as pd
import os
from datetime import datetime 
import copy
import numpy as np
import logging
from constants import (IGNORE)
# from data.aggregations.coinbase.constants import VALUE

# from data.aggregations.coinbase.constants import DATE
# from data.aggregations.coinbase.constants import DATE_CREATED

UNREALIZED = 'unrealized'
REALIZED = 'realized'
SOLD_INDEX = 'sold_transaciton'
BOUGHT_INDEX = 'bought_transaction'
TYPE = 'type'
USD_VALUE = 'usd_value'
COIN_BALANCE = 'coin_balance'
DATE_CREATED = 'created_at'
AMOUNT = 'amount'
NAME = 'name'
CURRENCY = 'currency'
RATE = 'rate'
TRANSACTION_KEYS = {
    TYPE : 'type',
    DATE_CREATED : 'created_at',
    USD_VALUE : 'native_amount',
    COIN_BALANCE : 'amount',
}
USD_BALANCE = 'usd_balance'
# TRADE = 'trade'
# ID = 'id'
# TRADE_ID = 'trade_id'
HOLDINGS = 'holdings'
TRANSACTION_TYPE = 'transaction_type'
BOUGHT = 'bought'
SOLD = 'sold'
AMOUNT = 'amount'
USD_VALUE = 'usd_value'
RATE_DIFF= 'rate_diff'
BOUGHT_RATE = 'bought_rate'
SOLD_RATE = 'sold_rate'
PURCHASED_VALUE = 'purchased_value'
PROFIT= 'profit'
INDEX = 'index'
SPOT_USD = '-USD'
PERCENT_CHANGE = 'percent change'

class wallet():
    def __init__(self, api_key, api_secret):
        self.realized_gains = 0
        self.unrealized_gains = 0
        self.balance = 0
        self.returns = 0
        # self.summary = {HOLDINGS : [], REALIZED_GAINS : 0}
        # self.ignore = ['ETH']
        self.ignore = IGNORE
        self.coin_profits = {}
        
        # Built in function to get account details from coinbase client.
        
        try:
            self.client = Client(api_key, api_secret)
            self.accounts = self.client.get_accounts()
            self.coins = self.get_transactions()
        except Exception as error:
            logging.error('Can not connect to Coinbase, check if website is down!')
            logging.error('Error : {}'.format(error))

        # Getting a list of our coins.
        


    def get_transactions(self):
        logging.info("Getting all account transactions")

        my_transactions = []
        # get all accounts that are returned.
        for account in self.accounts['data']:
            # if the currency is not in our ignore file.
            if account['id'] != account['currency'] and account['currency'] not in self.ignore:
                transactions = self.client.get_transactions(account['id'])
                for transaction in transactions['data']:
                    row = {
                        TYPE : transaction[TRANSACTION_KEYS[TYPE]],
                        DATE_CREATED : datetime.strptime(transaction[TRANSACTION_KEYS[DATE_CREATED]], '%Y-%m-%dT%XZ'),
                        USD_VALUE : float(transaction[TRANSACTION_KEYS[USD_VALUE]][AMOUNT]),
                        COIN_BALANCE : float(transaction[TRANSACTION_KEYS[COIN_BALANCE]][AMOUNT]),
                        NAME : account[CURRENCY],
                        # TRADE_ID : (transaction[TRADE][ID] if TRADE in transaction else None) 
                    }
                    my_transactions.append(row)
        df = pd.DataFrame(my_transactions)
        df[RATE] =   df[USD_VALUE] / df[COIN_BALANCE]
        logging.info("Created dataframe of transactions")

        self.df = df
    
    def filter_dates(self, first, last=None):
        if last != None:
            self.df = self.df[self.df[DATE_CREATED] <= pd.to_datetime(last)]
        date_filter = pd.to_datetime(first)
        # df = self.df
        self.df = self.df[self.df[DATE_CREATED] >= date_filter]
        

    def get_costbasis(self):
        # Settup
        logging.info("Calculating cost basis through FIFO")
        df = copy.deepcopy(self.df)
        df[TRANSACTION_TYPE] = df[USD_VALUE].apply(lambda x : BOUGHT if x >= 0 else SOLD)
    
        # Group by cryptocurrency
        grouped_df = df.groupby(NAME)

        transactions = []
        coin_summary = []
        for key, item in grouped_df:
            group = grouped_df.get_group(key)
            bought_coin = []
            sold_coins = []
            total_balance_usd = group[USD_VALUE].sum()
            for index, row in group.iterrows():
                trans_cost = {
                    COIN_BALANCE : row[COIN_BALANCE], 
                    RATE : row[RATE],
                    INDEX : index,
                    }
                if row[TRANSACTION_TYPE] == BOUGHT:
                    bought_coin.append(trans_cost)
                else:
                    sold_coins.append(trans_cost)

            logging.info(f"Coin is {key}")
            spot_rate = float(self.client.get_spot_price(currency_pair = (key+ SPOT_USD))[AMOUNT])
            
            usd_bought = group[group[TRANSACTION_TYPE] != SOLD][USD_VALUE].sum()
            usd_sold = abs(group[group[TRANSACTION_TYPE] == SOLD][USD_VALUE].sum())
            coin_value = group[COIN_BALANCE].sum() * spot_rate
            logging.info(f'spot_rate is {spot_rate}')
            logging.info(f'total amount of coins {group[COIN_BALANCE].sum()}')
            coin_summary.append({
                                    NAME : key , 
                                    USD_BALANCE : total_balance_usd , 
                                    COIN_BALANCE : round(group[COIN_BALANCE].sum() , 3),
                                    PERCENT_CHANGE : round((coin_value - total_balance_usd) / total_balance_usd * 100, 2),
                                    'USD Bought' : usd_bought,
                                    'USD Sold' : usd_sold,
                                    'Current Value' : round(coin_value , 3),
                                    'Diff Value' : round(coin_value - total_balance_usd  , 3),
                                    'Realized Value' : (coin_value - (usd_bought - usd_sold)) - total_balance_usd,
                                    'Spot Rate' : spot_rate}
                                    )
        logging.info("Creating cost basis dataframe")
        df = pd.DataFrame(transactions)
        self.coin_profits = coin_summary
        return df

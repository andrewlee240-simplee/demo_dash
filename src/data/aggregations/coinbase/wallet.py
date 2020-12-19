from coinbase.wallet.client import Client
import pandas as pd
import os
from datetime import datetime
import copy
import numpy as np
import logging
from constants import (IGNORE)
# from data.aggregations.coinbase.constants import DATE
# from data.aggregations.coinbase.constants import DATE_CREATED

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
class wallet():
    def __init__(self, api_key, api_secret):
        self.realized_gains = 0
        self.unrealized_gains = 0
        self.balance = 0
        self.returns = 0
        # self.summary = {HOLDINGS : [], REALIZED_GAINS : 0}
        self.ignore = IGNORE
        
        # Built in function to get account details from coinbase client.
        self.client = Client(api_key, api_secret)
        self.accounts = self.client.get_accounts()

        # Getting a list of our coins.
        self.coins = self.get_transactions()


    def get_transactions(self):
        logging.info("Getting all account transactions")

        my_transactions = []
        # get all accounts that are returned.
        for account in self.accounts['data']:
            # if the currency is not in our ignore file.
            if account['id'] != account['currency'] and account['currency'] not in self.ignore:
                transactions = self.client.get_transactions(account['id'])
                for transaction in transactions['data']:
                    # print(transaction)
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
        df[RATE] = df[USD_VALUE] / df[COIN_BALANCE]
        logging.info("Created dataframe of transactions")
        print("DF...")
        print(df[COIN_BALANCE])
        self.df = df
        return df

    def get_costbasis(self):
        # Settup
        logging.info("Calculating cost basis through FIFO")
        df = self.df
        df[TRANSACTION_TYPE] = df[USD_VALUE].apply(lambda x : BOUGHT if x >= 0 else SOLD)

        # Group by cryptocurrency
        grouped_df = df.groupby(NAME)
        leftover_list = []
        records = []
        coin_records = []
        sold_records = []
        for key, item in grouped_df:
            group = grouped_df.get_group(key)
            bought_coin = []
            sold_coins = []
            for index, row in group.iterrows():
                trans_cost = {
                    COIN_BALANCE : row[COIN_BALANCE], 
                    RATE : row[RATE],
                    INDEX : index,
                    }
                if row[TRANSACTION_TYPE] == BOUGHT:
                    bought_coin.insert(0, trans_cost)
                else:
                    sold_coins.insert(0, trans_cost)

            print(key)
            spot_rate = 1/float(self.client.get_spot_price(currency_pair = (key+ SPOT_USD))[AMOUNT])
            fifo_list, leftovers = fifo(bought_coin , sold_coins, spot_rate)

            realized_gains = 0
            unrealized_gains = 0
        # return all_records
            # print('fifo')
            for x in fifo_list:
                print(x)
            print('leftovers')
            for x in leftovers:
                print(x)
                print('\t', x[AMOUNT] * x[RATE_DIFF])
            print(key)
            print(fifo_list)
            print(leftovers)
            print('\tamount: ', amount)
            print('\tvalue: ' ,value)
        # Aggregate TransactionsW
        # return a dictionary of crypto classes after running some data cleans
        # crypto_class = {}
        # for x in cryptos:
        #     # Create different classes for each crypto type

        # return crypto_class

def fifo(bought, sold, spot_rate):
    #Run fifo method
    bought_iter = 0
    curr_bought = bought[bought_iter][COIN_BALANCE]
    fifo_list = []
    leftover = None
    # Lets do some checks and balances...
    total_sum = 0
    for trans in sold:
        total_sum += abs(trans[COIN_BALANCE])
    print("Total sold is : "  , total_sum)
    for trans in sold:
        
        curr_sold = abs(trans[COIN_BALANCE])
        # print('CoinBalance : ' , curr_sold , ' .. vs .. ' , curr_bought)

        while(curr_sold != 0):
            # print('\tCoinBalance : ' , curr_sold , ' .. vs .. ' , curr_bought)
            # if what we sold is greater than purchase
            # reduce from amount we sold then go to the next transaction where we purchased.
            # print('Curr_sold is ...' , curr_sold)
            if curr_sold > curr_bought:
                curr_sold -= curr_bought
                current_amount = curr_bought

                try:
                    bought_iter += 1
                    curr_bought = bought[bought_iter][COIN_BALANCE]
                except Exception as error:
                    logging.error('There are more sold than there were purchased !')
            else:
                # if the sold is smaller than the bought,
                curr_bought -= curr_sold
                current_amount = curr_sold
                # print('\tMove to the next in sold stacks (leave while loop)', current_amount)
                curr_sold = 0
            rate = bought[bought_iter][RATE]
            # print(f'Results : Sold - {curr_sold} ... {current_amount}')
            add_trans = create_transaction(current_amount, trans[RATE] ,rate, trans[INDEX])
            total_sum -= current_amount

            fifo_list.append(add_trans)
        # print('\tCurrent Amount Unaccounted for ' , total_sum)        
        # if we subtracted from a value that we already removed from.
        rate = bought[bought_iter][RATE]
        leftover = create_transaction(curr_bought, trans[RATE] , rate, bought[bought_iter][INDEX])
    print('\tCurrent Amount Unaccounted for ' , round(total_sum,4))  
    leftover_list = []
    if bought_iter != 0:
        bought_iter += 1
    if bought_iter < len(bought):
        for transaction in bought[bought_iter:]:
            # print('transaction[coin_Balance]' , transaction[COIN_BALANCE])
            add_trans = create_transaction(transaction[COIN_BALANCE] , spot_rate, transaction[RATE], transaction[INDEX])
            leftover_list.append(add_trans)
        if leftover is not None:    
            leftover_list.insert(0,leftover)
    
    return fifo_list, leftover_list

def create_transaction(amount, sold_rate, bought_rate, index):
    return {AMOUNT : amount , 
            SOLD_RATE : sold_rate, 
            BOUGHT_RATE : bought_rate,
            RATE_DIFF :  sold_rate - bought_rate,
            INDEX : index}
        
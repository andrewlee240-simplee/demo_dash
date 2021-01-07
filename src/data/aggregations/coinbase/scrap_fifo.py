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
            
            coin_value = group[COIN_BALANCE].sum() * spot_rate
            logging.info(f'spot_rate is {spot_rate}')
            logging.info(f'total amount of coins {group[COIN_BALANCE].sum()}')
            coin_summary.append({
                                    NAME : key , 
                                    USD_BALANCE : total_balance_usd , 
                                    COIN_BALANCE : round(group[COIN_BALANCE].sum() , 3),
                                    PERCENT_CHANGE : round((coin_value - total_balance_usd) / total_balance_usd , 3),
                                    'Current Value' : round(coin_value , 3),
                                    'Diff Value' : round(coin_value - total_balance_usd  , 3),
                                    'Spot Rate' : spot_rate}
                                    )
        logging.info("Creating cost basis dataframe")
        df = pd.DataFrame(transactions)
        self.coin_profits = coin_summary
        return df

    def get_costbasis_fifo(self):
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
            fifo_list, leftovers = fifo(bought_coin , sold_coins, spot_rate)

            coin_unrealized = 0
            coin_realized = 0
            for x in fifo_list:
                coin_realized += (x[AMOUNT] * x[RATE_DIFF]) 
                coin_value = {'value' : x[AMOUNT] * x[RATE_DIFF] , 'realized' : True , 'name' : key , SOLD_INDEX : x[SOLD_INDEX] , BOUGHT_INDEX : x[BOUGHT_INDEX]}
                transactions.append(coin_value)
            for x in leftovers:
                coin_unrealized += (x[AMOUNT] *  x[RATE_DIFF])
                coin_value = {'value' : x[AMOUNT] * x[RATE_DIFF] , 'realized' : False , 'name' : key , SOLD_INDEX : x[SOLD_INDEX] , BOUGHT_INDEX : x[BOUGHT_INDEX]}
                transactions.append(coin_value)

            
            coin_value = group[COIN_BALANCE].sum() * spot_rate
            logging.info(f'spot_rate is {spot_rate}')
            logging.info(f'total amount of coins {group[COIN_BALANCE].sum()}')
            coin_summary.append({
                                    NAME : key , 
                                    UNREALIZED : coin_unrealized , 
                                    REALIZED : coin_realized , 
                                    USD_BALANCE : total_balance_usd , 
                                    PERCENT_CHANGE : round((1 - (total_balance_usd - coin_unrealized) / total_balance_usd) * 100 , 2),
                                    "Current Value" : total_balance_usd + coin_unrealized,
                                    'True Value' : coin_value,
                                    'Diff Value' : round((coin_value - (total_balance_usd + coin_unrealized)) / coin_value  , 3),
                                    'Spot Rate' : spot_rate}
                                    )
        logging.info("Creating Fifo dataframe")
        fifo_df = pd.DataFrame(transactions)
        self.coin_profits = coin_summary
        self.fifo_df = fifo_df
        return fifo_df
    
    def coin_filter(self, coins):
        self.df = self.df[self.df[NAME].isin(coins)]
        return self.df



def fifo(bought, sold, spot_rate):
    #Run fifo method
    bought_iter = 0
    curr_bought = bought[bought_iter][COIN_BALANCE]
    fifo_list = []
    leftover = None
    # Lets do some checks and balances...
    total_sum = 0
    leftover_iter = 0
    for trans in sold:
        
        curr_sold = abs(trans[COIN_BALANCE])

        while(curr_sold != 0):
            logging.info(f'curr_sold : {curr_sold} curr_bought :{curr_bought}')
            if curr_sold > curr_bought:
                curr_sold -= curr_bought
                current_amount = curr_bought
                try:
                    bought_iter += 1
                    curr_bought = bought[bought_iter][COIN_BALANCE]
                except Exception as error:
                    logging.error(f'There are more sold than there were purchased! curr_sold : {curr_sold} curr_bought :{curr_bought}')
            elif curr_sold == curr_bought:
                logging.info("Sold and Bought are Equals")
                
                current_amount = curr_bought
                curr_sold = 0
                curr_bought = 0
                leftover_iter += 1
            else:
                # if the sold is smaller than the bought,
                curr_bought -= curr_sold
                current_amount = curr_sold
                leftover_iter += 1
                curr_sold = 0
            rate = bought[bought_iter][RATE]

            logging.info(f'adding transaction with current amount of  : {current_amount}')
            add_trans = create_transaction(current_amount, trans[RATE] ,rate, trans[INDEX], bought[bought_iter][INDEX])
            total_sum -= current_amount

            fifo_list.append(add_trans)

        rate = bought[bought_iter][RATE]
        
        if curr_bought > 0:
            logging.info(f"There are leftovers, is {curr_bought} not 0")
            leftover = create_transaction(curr_bought, trans[RATE] , rate, trans[INDEX], bought[bought_iter][INDEX])
            
    logging.info(f"Creating Leftover List {leftover_iter}")
    leftover_list = []
    if leftover_iter != 0:
        bought_iter += 1
    if leftover_iter < len(bought):
        for transaction in bought[leftover_iter:]:
            add_trans = create_transaction(transaction[COIN_BALANCE] , spot_rate, transaction[RATE], None , transaction[INDEX])
            leftover_list.append(add_trans)
        if leftover is not None:    
            leftover_list.insert(0,leftover)
    
    return fifo_list, leftover_list

def create_transaction(amount, sold_rate, bought_rate, sold_id , bought_id):

    logging.info(f'Transaction Profit (({round(sold_rate, 6)} - {round(bought_rate,6)}) * {round(amount,6)}) =  {(sold_rate - bought_rate) * amount}')
    adict = {AMOUNT : amount , 
            SOLD_RATE : sold_rate, 
            BOUGHT_RATE : bought_rate,
            RATE_DIFF :  sold_rate - bought_rate,
            SOLD_INDEX : sold_id,
            BOUGHT_INDEX : bought_id}
        
    return adict


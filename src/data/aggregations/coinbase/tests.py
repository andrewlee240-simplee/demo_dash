from pandas.core import groupby
import constants as const
import pandas as pd
import crypto_class as cc
from dotenv import load_dotenv
from os import path

load_dotenv()
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Need to account for transfers to a different crypto
def get_portfolio():
    my_wallet = cc.wallet()
    summary = my_wallet.get_summary()
    if path.exists("data/crypto_returns/crypto_return.csv"):
        summary.to_csv('data/crypto_returns/crypto_return.csv', mode='a', header=False)
    else:
        summary.to_csv("data/crypto_returns/crypto_return.csv")
    # print(summary)
    my_wallet.get_costbasis()

def read_file(filename):
    portfoio = pd.read_csv(filename)
    grouped_date = portfoio.groupby(by='time')
    
    net_returns = []
    for date, group in grouped_date:
        net_returns.append({'date' : date , 'net_return' : group['net_return'].sum()})
        # print(group['net_return'].sum())
    print(portfoio)

    # for x in net_returns:
    #     print(x)
get_portfolio()
# read_file('data/crypto_returns/crypto_return.csv')

# Need to account for fees when pikurchasing
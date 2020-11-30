import constants as const
import pandas as pd
import crypto_class as cc
from dotenv import load_dotenv
from os import path

load_dotenv()
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Need to account for transfers to a different crypto

my_wallet = cc.wallet()
summary = my_wallet.get_summary()
if path.exists("data/crypto_returns/crypto_return.csv"):
    summary.to_csv('data/crypto_returns/crypto_return.csv', mode='a', header=False)
else:
    summary.to_csv("data/crypto_returns/crypto_return.csv")
    
my_wallet.get_costbasis()

# def read_file(filename):
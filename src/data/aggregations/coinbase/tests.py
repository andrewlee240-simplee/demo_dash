import constants as const
import pandas as pd
import crypto_class as cc
from dotenv import load_dotenv
import os

load_dotenv()
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

my_wallet = cc.wallet()
my_wallet.get_summary()
import dash
import pandas as pd
import os
from dotenv import load_dotenv


# load and create connections to apis
def connect_and_load():
    load_dotenv()
    

if __name__ == "__main__":
    # Load api keys
    load_dotenv()

    print(os.getenv('FINNHUB'))
    print(os.getenv('ALPACA'))
    pass
import alpaca_trade_api
import pandas as pd
import alpaca_trade_api as alpaca
import os


class alpaca_account:
    def __init__(self, key=None, secret_key=None):
        if key is None:
            key = os.getenv('APCA_API_KEY_ID')
        if secret_key is None:
            secret_key = os.getenv('APCA_API_SECRET_KEY')           
        self.api = alpaca.REST(key, secret_key, base_url='https://paper-api.alpaca.markets')
        self.account = self.api.get_account()
        self.time_zone = 'America/New_York'

    def get_bar(self, timeframe, symbols, start_time, end_time):
        '''
            https://alpaca.markets/docs/api-documentation/api-v2/market-data/bars/
            :param timeframe: One of minute, 1Min, 5Min, 15Min, day or 1D. minute
            is an alias of 1Min. Similarly, day is of 1D.
        '''
        if type(symbols) != list:
            symbols = [symbols]
        
        start=pd.Timestamp(start_time, tz=self.time_zone).isoformat()
        end=pd.Timestamp(end_time, tz=self.time_zone).isoformat()
        result = self.api.get_barset(symbols, timeframe, start=start, end=end).df

        return result

    
        
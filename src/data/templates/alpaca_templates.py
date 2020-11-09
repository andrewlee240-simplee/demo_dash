import pandas as pd
import alpaca_trade_api as alpaca
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('APCA_API_KEY_ID')
secret_key = os.getenv('APCA_API_SECRET_KEY')           
api = alpaca.REST(key, secret_key, base_url='https://paper-api.alpaca.markets')
account = api.get_account()
print(account)

NY = 'America/New_York'
start=pd.Timestamp('2020-08-01', tz=NY).isoformat()
end=pd.Timestamp('2020-08-30', tz=NY).isoformat()
print(api.get_barset(['AAPL', 'GOOG'], 'day', start=start, end=end).df)

# Minute data example
start=pd.Timestamp('2020-08-28 9:30', tz=NY).isoformat()
end=pd.Timestamp('2020-08-28 16:00', tz=NY).isoformat()
print(api.get_barset('AAPL', 'minute', start=start, end=end).df)
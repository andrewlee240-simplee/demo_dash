import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

pd.set_option('display.max_colwidth', -1)

# print(msft.history(period='max', interval='5d'))

# print(msft.earnings)
# print("---")
# print(msft.institutional_holders)

# print(msft.recommendations[-10:].to_string())


# '''
# Using Groupbys
# '''


# print(group_rec)
# print()
'''RATINGS = {
    'Strong Buy' : 1, 
    'Buy' : 2, 
    'Hold' : 3, 
    'Underperform' : 4 , 
    'Sell' : 5}
WEIGHTS = {
    'Overweight' : 5,
    'Equal-Weight' : 3,
    'Underweight' : 1
}
MARKETS = {
    'Market Outperform' : 1,
    'Market Perform' : 3,
    'Underperform' : 5
}
SECTOR = {
    'Sector Outperform' : 1,
    'Sector Perform' : 3 , 
    'Sector '
}
OUTLOOK = {
    'Positive' : 1,
    'Neutral' : 3,
    'Negative' : 5
}
'''

# Market Outperform

# Overweight

# Neutral
# Buy
# Hold
# Sector Weight
# Long-term Buy
# Equal-Weight
# Positive
# Strong Buy
# Negative
# Underperform
# Sector Perform
# Long-Term Buy
# Outperform
# Equal-weight
# Perform
# Sector Outperform
# Market Perform
# Reduce
# Sell
# Underweight

ACTION = {
    'init' : 3 , 
    'main' : 3 , 
    'reit' : 3,
    'up'   : 1,
    'down' : 5,
    }

class stock():
    def __init__(self, symbol):
        self.stock = yf.Ticker(symbol)
    
    def clean_recommendations(self):
        self.recommendations = self.stock.recommendations
        self.recommendations['quarter'] = pd.PeriodIndex(self.recommendations.index, freq='Q') # Split dates into year and quarter 
        self.recommendations['change'] = self.recommendations['Action'].replace(ACTION)
        self.firms_rec = self.recommendations.Firm.unique()
        group_rec = self.recommendations.groupby('Firm').agg(list)
        print(group_rec[['change', 'quarter']].to_string())



    def recs(self):
        self.recs = self.stock.recommendations
        print(self.recs)

msft = stock('msft')
msft.clean_recommendations()


# fig = px.scatter(msft_rec, x="quarters", y="Action")
# fig.show()




# fig = px.line(msft_rec, x="quarters", y="lifeExp", color='country')
# fig.show()
'''
# get stock info
msft.info

# get historical market data
hist = msft.history(period="max")

# show actions (dividends, splits)
msft.actions

# show dividends
msft.dividends

# show splits
msft.splits

# show financials
msft.financials
msft.quarterly_financials

# show major holders
msft.major_holders

# show institutional holders
msft.institutional_holders

# show balance sheet
msft.balance_sheet
msft.quarterly_balance_sheet

# show cashflow
msft.cashflow
msft.quarterly_cashflow

# show earnings
msft.earnings
msft.quarterly_earnings

# show sustainability
msft.sustainability

# show analysts recommendations
msft.recommendations

# show next event (earnings, etc)
msft.calendar

# show ISIN code - *experimental*
# ISIN = International Securities Identification Number
msft.isin

# show options expirations
msft.options

# get option chain for specific expiration
# opt = msft.option_chain('YYYY-MM-DD')
# data available via: opt.calls, opt.puts

'''
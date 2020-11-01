import gs_quant.timeseries as ts
from gs_quant.timeseries import Window

x = ts.generate_series(1000)           # Generate random timeseries with 1000 observations
vol = ts.volatility(x, Window(22, 0))  # Compute realized volatility using a window of 22 and a ramp up value of 0
vol.tail()                             # Show last few values

print(vol.tail)
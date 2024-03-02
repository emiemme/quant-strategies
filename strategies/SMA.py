import pandas as pd
import yfinance as yf
import numpy as np


def download_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return stock_data

def generate_signals(data):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Create a short simple moving average over the short window
    signals['short_mavg'] = data['Close'].rolling(window=40, min_periods=1, center=False).mean()

    # Create a long simple moving average over the long window
    signals['long_mavg'] = data['Close'].rolling(window=100, min_periods=1, center=False).mean()


    conditions  = [ signals['short_mavg'][40:] > signals['long_mavg'][40:], signals['short_mavg'][40:] < signals['long_mavg'][40:], signals['short_mavg'][40:] == signals['long_mavg'][40:] ]
    choices     = [ 1.0, -1.0, 0.0 ]
        
    signals['signal'][40:] = np.select(conditions, choices, default=0.0)
    # Create signals
    #signals['signal'][40:] = np.where(signals['short_mavg'][40:] > signals['long_mavg'][40:], 1.0, 0.0)
    print(signals['signal'][40:])
    # Generate trading orders
    signals['positions'] = signals['signal'].diff()
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    signals = generate_signals(stock_data)
    return stock_data, signals
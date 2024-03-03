import pandas as pd
import yfinance as yf
import numpy as np


def download_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return stock_data

def generate_signals(data):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    rsi_period = 14
    rsi_buy_threshold = 30
    rsi_sell_threshold = 70
    # Calculate the RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    conditions  = [ rsi < rsi_buy_threshold, rsi > rsi_sell_threshold]
    choices     = [ 1.0, -1.0 ]
        
    signals['signal'] = np.select(conditions, choices, default=0.0)
    # Create signals
    #print(signals['signal'])
    # Generate trading orders
    signals['positions'] = signals['signal'].diff()
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    signals = generate_signals(stock_data)
    return stock_data, signals
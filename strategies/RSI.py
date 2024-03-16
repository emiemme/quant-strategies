import pandas as pd
import yfinance as yf
import numpy as np


def download_stock_data(symbol, start_date, end_date):
    try:
        stock_data = yf.download(symbol, start=start_date, end=end_date)
        return stock_data
    except Exception as e:
        print(f"Error downloading stock data: {e}")
        return None

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
    rs = gain / (loss + 1e-8)  # avoid division by zero
    rsi = 100 - (100 / (1 + rs))

    conditions  = [ rsi < rsi_buy_threshold, rsi > rsi_sell_threshold]
    choices     = [ 1.0, -1.0 ]

     # Create signals
    signals['signal'] = np.select(conditions, choices, default=0.0)

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    if stock_data is not None:
        signals = generate_signals(stock_data)
        return stock_data, signals
    else:
        return None, None
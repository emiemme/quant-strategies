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

def generate_signals(symbol,data):
    if not isinstance(data, pd.DataFrame) or 'Close' not in data.columns:
        raise ValueError("Invalid input data")
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Create a short simple moving average over the short window
    signals['short_mavg'] = data[('Close', symbol)].rolling(window=40, min_periods=1, center=False).mean()

    # Create a long simple moving average over the long window
    signals['long_mavg'] = data[('Close', symbol)].rolling(window=100, min_periods=1, center=False).mean()


    conditions  = [ signals['short_mavg'][40:] > signals['long_mavg'][40:], signals['short_mavg'][40:] < signals['long_mavg'][40:], signals['short_mavg'][40:] == signals['long_mavg'][40:] ]
    choices     = [ 1.0, -1.0, 0.0 ]

    # Create signals
    signals['signal'][40:] = np.select(conditions, choices, default=0.0)

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()
    return signals

def sma_20_50_200_indicators(symbol,data):
    sma = pd.DataFrame(index=data.index)
    sma['SMA_20'] = data[('Close', symbol)].rolling(window=20, min_periods=1, center=False).mean()

    sma['SMA_50']  = data[('Close', symbol)].rolling(window=50, min_periods=1, center=False).mean()
    sma['SMA_200'] = data[('Close', symbol)].rolling(window=200, min_periods=1, center=False).mean()

    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    for i in range(1, len(data.index)):
        prev_idx = data.index[i - 1]
        curr_idx = data.index[i]

        if sma.loc[prev_idx, 'SMA_50'] > sma.loc[prev_idx, 'SMA_200'] and sma.loc[curr_idx, 'SMA_50'] < sma.loc[curr_idx, 'SMA_200']:
            signals.loc[curr_idx, 'signal'] = -1

        elif sma.loc[prev_idx, 'SMA_50'] < sma.loc[prev_idx, 'SMA_200'] and sma.loc[curr_idx, 'SMA_50'] > sma.loc[curr_idx, 'SMA_200']:
            signals.loc[curr_idx, 'signal'] = 1

        else:
            if sma.loc[prev_idx, 'SMA_50'] > sma.loc[prev_idx, 'SMA_20'] and sma.loc[curr_idx, 'SMA_50'] < sma.loc[curr_idx, 'SMA_20']:
                signals.loc[curr_idx, 'signal'] = -1
            elif sma.loc[prev_idx, 'SMA_50'] < sma.loc[prev_idx, 'SMA_20'] and sma.loc[curr_idx, 'SMA_50'] > sma.loc[curr_idx, 'SMA_20']:
                signals.loc[curr_idx, 'signal'] = 1
                           
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    if stock_data is not None:
        signals = generate_signals(symbol,stock_data)
        return stock_data, signals
    else:
        return None, None
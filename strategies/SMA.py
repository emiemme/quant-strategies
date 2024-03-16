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
    if not isinstance(data, pd.DataFrame) or 'Close' not in data.columns:
        raise ValueError("Invalid input data")
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Create a short simple moving average over the short window
    signals['short_mavg'] = data['Close'].rolling(window=40, min_periods=1, center=False).mean()

    # Create a long simple moving average over the long window
    signals['long_mavg'] = data['Close'].rolling(window=100, min_periods=1, center=False).mean()


    conditions  = [ signals['short_mavg'][40:] > signals['long_mavg'][40:], signals['short_mavg'][40:] < signals['long_mavg'][40:], signals['short_mavg'][40:] == signals['long_mavg'][40:] ]
    choices     = [ 1.0, -1.0, 0.0 ]

    # Create signals
    signals['signal'][40:] = np.select(conditions, choices, default=0.0)

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()
    return signals

def sma_20_50_200_indicators(data):
    sma = pd.DataFrame(index=data.index)
    sma['SMA_20'] = data['Close'].rolling(window=20, min_periods=1, center=False).mean()

    sma['SMA_50']  = data['Close'].rolling(window=50, min_periods=1, center=False).mean()
    sma['SMA_200'] = data['Close'].rolling(window=200, min_periods=1, center=False).mean()

    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    df_len = len(data)
    for row in range(1, df_len):
        if sma['SMA_50'].iloc[row -1] > sma['SMA_200'].iloc[row-1] and sma['SMA_50'].iloc[row] < sma['SMA_200'].iloc[row]:
            signals['signal'].iat[row] = -1
        elif sma['SMA_50'].iloc[row -1] < sma['SMA_200'].iloc[row-1] and sma['SMA_50'].iloc[row] > sma['SMA_200'].iloc[row]:
            signals['signal'].iat[row] = 1
        else:
            if sma['SMA_50'].iloc[row -1] > sma['SMA_20'].iloc[row -1] and sma['SMA_50'].iloc[row] < sma['SMA_20'].iloc[row]:
                signals['signal'].iat[row] = -1
            elif sma['SMA_50'].iloc[row -1] < sma['SMA_20'].iloc[row -1] and sma['SMA_50'].iloc[row] > sma['SMA_20'].iloc[row]:
                signals['signal'].iat[row] = 1
                           
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    if stock_data is not None:
        signals = generate_signals(stock_data)
        return stock_data, signals
    else:
        return None, None
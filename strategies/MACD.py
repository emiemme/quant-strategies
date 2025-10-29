import pandas as pd
import yfinance as yf
import pandas_ta as ta

def download_stock_data(symbol, start_date, end_date):
    try:
        stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        return stock_data
    except Exception as e:
        print(f"Error downloading stock data: {e}")
        return None

def generate_signals(symbol,data):
    if not isinstance(data, pd.DataFrame) or 'Close' not in data.columns:
        raise ValueError("Invalid input data")
    # Calculate MACD
    short_term = 12
    long_term = 26
    signal_period = 9

    # Calculate short-term and long-term EMAs
    macd = ta.macd(data[('Close', symbol)], fast=short_term, slow=long_term, signal=signal_period)
    macd_line = macd['MACD_12_26_9']
    signal_line = macd['MACDs_12_26_9']

    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    for i in range(1, len(data.index)):
        prev_idx = data.index[i - 1]
        curr_idx = data.index[i]

        if (macd_line.loc[prev_idx] < 0) and (macd_line.loc[curr_idx] > 0):
            signals.loc[curr_idx, 'signal'] = 1.0
        elif (macd_line.loc[prev_idx] > 0) and (macd_line.loc[curr_idx] < 0):
            signals.loc[curr_idx, 'signal'] = -1.0
        else:
            if macd_line.loc[curr_idx] > signal_line.loc[curr_idx]:
                signals.loc[curr_idx, 'signal'] = 1.0
            elif macd_line.loc[curr_idx] < signal_line.loc[curr_idx]:
                signals.loc[curr_idx, 'signal'] = -1.0
    
    signals['positions'] = signals['signal'].diff()
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    if stock_data is not None:
        signals = generate_signals(symbol,stock_data)
        return stock_data, signals
    else:
        return None, None
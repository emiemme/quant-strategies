import pandas as pd
import yfinance as yf
import pandas_ta as ta

def download_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return stock_data


def generate_signals(data):
    # Calculate MACD
    short_term = 12
    long_term = 26
    signal_period = 9

    # Calculate short-term and long-term EMAs
    macd = ta.macd(data['Adj Close'], fast=short_term, slow=long_term, signal=signal_period)
    macd_line = macd['MACD_12_26_9']
    signal_line = macd['MACDs_12_26_9']

    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    df_len = len(data)
    for row in range(1, df_len):
        if macd_line.iloc[row-1] < 0 and macd_line.iloc[row] > 0:
            signals['signal'].iat[row] = 1.0
        elif macd_line.iloc[row-1] > 0  and macd_line.iloc[row] < 0:
            signals['signal'].iat[row] = -1.0
        else:
            if macd_line.iloc[row] > signal_line.iloc[row]:
                signals['signal'].iat[row] = 1.0
            elif macd_line.iloc[row] < signal_line.iloc[row]:
                signals['signal'].iat[row] = -1.0
    
    signals['positions'] = signals['signal'].diff()
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    signals = generate_signals(stock_data)
    return stock_data, signals
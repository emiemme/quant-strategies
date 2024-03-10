import pandas as pd
import yfinance as yf
import pandas_ta as ta
from strategies import RSI
from strategies import MACD

def download_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return stock_data

def macd_indicators(data):
    # Calculate MACD
    short_term = 12
    long_term = 26
    signal_period = 9

    # Calculate short-term and long-term EMAs
    macd = ta.macd(data['Adj Close'], fast=short_term, slow=long_term, signal=signal_period)
    macd_line = macd['MACD_12_26_9']
    signal_line = macd['MACDs_12_26_9']

    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    df_len = len(data)
    for row in range(1, df_len):
        if macd_line.iloc[row-1] < 0 and macd_line.iloc[row] > 0:
            signals['signal'].iat[row] = 1
        elif macd_line.iloc[row-1] > 0  and macd_line.iloc[row] < 0:
            signals['signal'].iat[row] = -1
        else:
            if macd_line.iloc[row] > signal_line.iloc[row]:
                signals['signal'].iat[row] = 1
            elif macd_line.iloc[row] < signal_line.iloc[row]:
                signals['signal'].iat[row] = -1
    return signals

def sma_indicators(data):
    sma = pd.DataFrame(index=data.index)
    #sma['SMA_10'] = data['Close'].rolling(window=10, min_periods=1, center=False).mean()
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

def generate_signals(data):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    macd_signals =  macd_indicators(data)
    sma_signals  = sma_indicators(data)
    
    buyFlag = False
    sellFlag = False
    df_len = len(data)
    for row in range(1, df_len):
        if sma_signals['signal'].iloc[row] == 1:
            buyFlag = True
            sellFlag = False
        elif sma_signals['signal'].iloc[row] == -1:
            buyFlag = False
            sellFlag = True
    
        if buyFlag == True:
            if macd_signals['signal'].iloc[row] == 1:
                signals['signal'].iat[row] = 1
        elif sellFlag == True:   
            if macd_signals['signal'][row] == -1:
                signals['signal'].iat[row] = -1  

        
 
    signals['positions'] = signals['signal'].diff()
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    signals = generate_signals(stock_data)
    #print(signals)
    return stock_data, signals
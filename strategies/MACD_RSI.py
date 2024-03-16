import pandas as pd
import yfinance as yf
import pandas_ta as ta
import numpy as np
from strategies import RSI
from strategies import MACD

def download_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date, interval="1d")
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


def rsi_indicators(data):
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

def generate_signals(data):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    macd_signals =  macd_indicators(data)
    rsi_signals  = rsi_indicators(data)
    
    buyFlag = False
    sellFlag = False
    df_len = len(data)
    for row in range(1, df_len):
        if rsi_signals['signal'].iloc[row] == 1:
            buyFlag = True
            sellFlag = False
        elif rsi_signals['signal'].iloc[row] == -1:
            buyFlag = False
            sellFlag = True
    
        if buyFlag == True:
            if macd_signals['signal'].iloc[row] == 1:
                signals['signal'].iat[row] = 1  
        elif sellFlag == True:   
            if macd_signals['signal'].iloc[row] == -1:
                signals['signal'].iat[row] = -1  

        
 
    signals['positions'] = signals['signal'].diff()
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    signals = generate_signals(stock_data)
    #print(signals)
    return stock_data, signals
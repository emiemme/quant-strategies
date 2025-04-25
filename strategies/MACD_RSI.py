import pandas as pd
import yfinance as yf
from strategies import RSI
from strategies import MACD

def download_stock_data(symbol, start_date, end_date):
    try:
        stock_data = yf.download(symbol, start=start_date, end=end_date, interval="1d")
        return stock_data
    except Exception as e:
        print(f"Error downloading stock data: {e}")
        return None

def generate_signals(symbol,data):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    macd_signals =  MACD.generate_signals(symbol,data)
    rsi_signals  = RSI.generate_signals(symbol,data)
    
    buyFlag = False
    sellFlag = False
    for i in range(1, len(data.index)):
        idx = data.index[i]

        if rsi_signals.loc[idx, 'signal'] == 1:
            buyFlag = True
            sellFlag = False
        elif rsi_signals.loc[idx, 'signal'] == -1:
            buyFlag = False
            sellFlag = True

        if buyFlag:
            if macd_signals.loc[idx, 'signal'] == 1:
                signals.loc[idx, 'signal'] = 1
        elif sellFlag:
            if macd_signals.loc[idx, 'signal'] == -1:
                signals.loc[idx, 'signal'] = -1

        
 
    signals['positions'] = signals['signal'].diff()
    return signals

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    if stock_data is not None:
        signals = generate_signals(symbol,stock_data)
        return stock_data, signals
    else:
        return None, None
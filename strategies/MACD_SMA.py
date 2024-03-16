import pandas as pd
import yfinance as yf
import pandas_ta as ta
from strategies import SMA
from strategies import MACD

def download_stock_data(symbol, start_date, end_date):
    try:
        stock_data = yf.download(symbol, start=start_date, end=end_date)
        return stock_data
    except Exception as e:
        print(f"Error downloading stock data: {e}")
        return None


def generate_signals(data):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    macd_signals =  MACD.generate_signals(data)
    sma_signals  =  SMA.sma_20_50_200_indicators(data)
    
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
    if stock_data is not None:
        signals = generate_signals(stock_data)
        return stock_data, signals
    else:
        return None, None
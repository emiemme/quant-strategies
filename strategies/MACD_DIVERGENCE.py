import pandas as pd
import yfinance as yf
import pandas_ta as ta

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
    
    close = data[('Close', symbol)]

    # Calculate MACD
    short_term = 12
    long_term = 26
    signal_period = 9

    # Calculate short-term and long-term EMAs
    macd = ta.macd(data[('Close', symbol)], fast=short_term, slow=long_term, signal=signal_period)
    macd_line = macd['MACD_12_26_9']
    signal_line = macd['MACDs_12_26_9']

    # Calcolo massimi e minimi locali
    def local_min(series):
        return (series.shift(1) > series) & (series.shift(-1) > series)

    def local_max(series):
        return (series.shift(1) < series) & (series.shift(-1) < series)

    price_min_idx = close[local_min(close)].index
    price_max_idx = close[local_max(close)].index
    macd_min_idx = macd_line[local_min(macd_line)].index
    macd_max_idx = macd_line[local_max(macd_line)].index

    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    lookback = 10  # giorni per cercare divergenze recenti

    for i in range(lookback, len(close)):
        curr_idx = close.index[i]

        # Trova gli ultimi due minimi/massimi locali
        recent_price_min = [idx for idx in price_min_idx if idx < curr_idx][-2:]
        recent_macd_min = [idx for idx in macd_min_idx if idx < curr_idx][-2:]
        recent_price_max = [idx for idx in price_max_idx if idx < curr_idx][-2:]
        recent_macd_max = [idx for idx in macd_max_idx if idx < curr_idx][-2:]

        # Divergenza rialzista → prezzo nuovi minimi, MACD no
        if len(recent_price_min) == 2 and len(recent_macd_min) == 2:
            p1, p2 = close.loc[recent_price_min]
            m1, m2 = macd_line.loc[recent_macd_min]
            if p2 < p1 and m2 > m1:
                signals.loc[curr_idx, 'signal'] = 1.0

        # Divergenza ribassista → prezzo nuovi massimi, MACD no
        if len(recent_price_max) == 2 and len(recent_macd_max) == 2:
            p1, p2 = close.loc[recent_price_max]
            m1, m2 = macd_line.loc[recent_macd_max]
            if p2 > p1 and m2 < m1:
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
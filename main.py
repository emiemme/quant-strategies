import sys
import importlib
from fredapi import Fred
from datetime import datetime
import pandas as pd

def get_macro_data_from_fred(series_ids, start_date, end_date, api_key):
    fred = Fred(api_key=api_key)
    data = pd.DataFrame()
    for name, series_id in series_ids.items():
        data[name] = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
    return data

def get_strategy(strategy_name):
    """Import and return a strategy module"""
    try:
        return importlib.import_module(f'strategies.{strategy_name}')
    except ImportError as e:
        print(f"Error importing strategy '{strategy_name}': {e}")
        return None

def backtest_strategy(strategy_name, symbol, start_date, end_date, macro_data, initial_capital):
    """Backtest a strategy and return the portfolio"""
    strategy = get_strategy(strategy_name)
    if (strategy is None):
        return None
    try:
        stock_data, signals = strategy.get_signals(symbol, start_date, end_date)
        #return simple_backtest.backtest_strategy_portfolio_sim(signals, stock_data, symbol, initial_capital)
        simple_backtest = importlib.import_module('backtest.simple_backtest')
        return simple_backtest.backtest_strategy_portfolio_sim(signals, stock_data, symbol, initial_capital,0.0019, 5, True, True, macro_data)
    except Exception as e:
        print(f"Error backtesting strategy '{strategy_name}': {e}")
        return None

if __name__ == "__main__":
    symbol = 'INTC'
    start_date = '2025-07-01'
    end_date = datetime.today().strftime('%Y-%m-%d')
    share_to_buy = 1
    initial_capital = 15000
    #STRATEGIES = ['SMA', 'RSI', 'MACD','MACD_SMA','MACD_RSI', 'MACD_DIVERGENCE']
    STRATEGIES = ['SMA','RSI','MACD_DIVERGENCE']


    # Add custom modules to the path
    try:
        sys.path.insert(0, 'strategies/')
        sys.path.insert(0, 'backtest/')
        #global simple_backtest
        #simple_backtest = importlib.import_module('backtest.simple_backtest')
    except Exception as e:
        print(f"Error importing custom modules: {e}")
        sys.exit(1)


    api_key = 'a5f3c579eb109f4c64bf918052bd1147'

    series_ids = {
        'GDP': 'GDP',              # GDP reale USA trimestrale
        'CPI': 'CPIAUCSL',          # Indice prezzi al consumo
        'Unemployment': 'UNRATE'    # Tasso di disoccupazione
    }

    macrodata_t = importlib.import_module('strategies.risk_mng')
    macro_data = get_macro_data_from_fred(series_ids, start_date, end_date, api_key)
    print(macro_data.tail())

    last_macro = macro_data.iloc[-1]
    risk_pct = macrodata_t.adjust_risk_based_on_macro(last_macro)
    risk_pct_vix = macrodata_t.adjust_risk_based_on_macro_and_vix(last_macro,24.84)
    print(f"Rischio suggerito: {risk_pct*100:.2f}%")
    print(f"Rischio suggerito con Vix: {risk_pct_vix*100:.2f}%")


    # Backtest each strategy and print the portfolio
    summary_rows = []
    for strategy_name in STRATEGIES:
        portfolio = backtest_strategy(strategy_name, symbol, start_date, end_date, macro_data, initial_capital)
        if portfolio is not None:
            last_row = portfolio.tail(1).copy()
            last_row['strategy'] = strategy_name
            summary_rows.append(last_row)
    summary_df = pd.concat(summary_rows)      
    summary_df = summary_df[['strategy'] + [col for col in summary_df.columns if col != 'strategy']]   
    print(summary_df)
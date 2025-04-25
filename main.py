import sys
import importlib
from datetime import datetime
import pandas as pd


def get_strategy(strategy_name):
    """Import and return a strategy module"""
    try:
        return importlib.import_module(f'strategies.{strategy_name}')
    except ImportError as e:
        print(f"Error importing strategy '{strategy_name}': {e}")
        return None

def backtest_strategy(strategy_name, symbol, start_date, end_date, shares_to_buy, initial_capital):
    """Backtest a strategy and return the portfolio"""
    strategy = get_strategy(strategy_name)
    if (strategy is None):
        return None
    try:
        stock_data, signals = strategy.get_signals(symbol, start_date, end_date)
        return simple_backtest.backtest_strategy_portfolio_sim(signals, stock_data, symbol, shares_to_buy, initial_capital)
    except Exception as e:
        print(f"Error backtesting strategy '{strategy_name}': {e}")
        return None

if __name__ == "__main__":
    symbol = 'SWDA.MI'
    start_date = '2018-01-01'
    end_date = datetime.today().strftime('%Y-%m-%d')
    share_to_buy = 1
    initial_capital = 1000
    STRATEGIES = ['SMA', 'RSI', 'MACD','MACD_SMA','MACD_RSI']

    # Add custom modules to the path
    try:
        sys.path.insert(0, 'strategies/')
        sys.path.insert(0, 'backtest/')
        global simple_backtest
        simple_backtest = importlib.import_module('backtest.simple_backtest')
    except Exception as e:
        print(f"Error importing custom modules: {e}")
        sys.exit(1)

    # Backtest each strategy and print the portfolio
    summary_rows = []
    for strategy_name in STRATEGIES:
        portfolio = backtest_strategy(strategy_name, symbol, start_date, end_date, share_to_buy, initial_capital)
        if portfolio is not None:
            last_row = portfolio.tail(1).copy()
            last_row['strategy'] = strategy_name
            summary_rows.append(last_row)
    summary_df = pd.concat(summary_rows)      
    summary_df = summary_df[['strategy'] + [col for col in summary_df.columns if col != 'strategy']]   
    print(summary_df)
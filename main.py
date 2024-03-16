import sys
import importlib

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
    if strategy is None:
        return None
    try:
        stock_data, signals = strategy.get_signals(symbol, start_date, end_date)
        return simple_backtest.backtest_strategy_portfolio_sim(signals, stock_data, shares_to_buy, initial_capital)
    except Exception as e:
        print(f"Error backtesting strategy '{strategy_name}': {e}")
        return None

if __name__ == "__main__":
    symbol = 'ADA-USD'
    start_date = '2023-01-01'
    end_date = '2024-07-01'
    share_to_buy = 100
    initial_capital = 1000
    STRATEGIES = ['SMA', 'RSI', 'MACD', 'MACD_SMA', 'MACD_RSI']

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
    for strategy_name in STRATEGIES:
        portfolio = backtest_strategy(strategy_name, symbol, start_date, end_date, share_to_buy, initial_capital)
        if portfolio is not None:
            print(f'Portfolio for {strategy_name}:')
            print(portfolio.tail(1))
            print()
import sys
sys.path.insert(0, 'strategies/')
sys.path.insert(0, 'backtest/')
from strategies import SMA
from strategies import RSI
from strategies import MACD
from strategies import MACD_SMA
from strategies import MACD_RSI
from backtest import simple_backtest


if __name__ == "__main__":
    symbol = 'NVDA'
    start_date = '2023-01-01'
    end_date = '2024-03-01'

    stock_data, signals = SMA.get_signals(symbol, start_date, end_date)

    #portfolio = simple_backtest.backtest_strategy(signals,stock_data,0.01,1000)
    portfolio = simple_backtest.backtest_strategy_portfolio_sim(signals,stock_data,0.1,1000)
    # Print the portfolio
    print(portfolio)   

    stock_data, signals = RSI.get_signals(symbol, start_date, end_date)
    portfolio = simple_backtest.backtest_strategy_portfolio_sim(signals,stock_data,0.1,1000)
    # Print the portfolio
    print(portfolio)   

    stock_data, signals = MACD.get_signals(symbol, start_date, end_date)
    portfolio = simple_backtest.backtest_strategy_portfolio_sim(signals,stock_data,0.1,1000)
    # Print the portfolio
    print(portfolio)   

    stock_data, signals = MACD_SMA.get_signals(symbol, start_date, end_date)
    portfolio = simple_backtest.backtest_strategy_portfolio_sim(signals,stock_data,0.1,1000)
    # Print the portfolio
    print(portfolio)  

    stock_data, signals = MACD_RSI.get_signals(symbol, start_date, end_date)
    portfolio = simple_backtest.backtest_strategy_portfolio_sim(signals,stock_data,0.1,1000)
    # Print the portfolio
    print(portfolio)  
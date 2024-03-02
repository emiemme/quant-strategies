import pandas as pd

def backtest_strategy(signals, backtest_data, initial_capital=10000, commissions=0.02):
    current_capital = initial_capital
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    
    for index, row in signals.iterrows():
        #print(index, row["signal"])
       print( backtest_data.loc[index,'Adj Close'])
    positions['stock'] = 10 * signals['signal']   # Buy 100 shares on each buy signal
    # Initialize the portfolio with value owned
    portfolio = positions.multiply(backtest_data['Adj Close'], axis=0)

    # Store the difference in shares owned
    pos_diff = positions.diff()

    # Add 'cash' to portfolio
    portfolio['cash'] = initial_capital - (pos_diff.multiply(backtest_data['Adj Close'], axis=0)).cumsum()

    # Add 'total' to portfolio
    portfolio['total'] = portfolio['cash'] + portfolio['stock']
    portfolio['P/L %'] = ((portfolio['total']/initial_capital) - 1) *100

    return portfolio

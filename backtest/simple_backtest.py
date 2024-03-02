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


def backtest_strategy_portfolio_sim(signals, backtest_data, share_to_buy = 1, initial_capital=1000, commissions=0.002):
    current_capital = initial_capital
    portfolio = pd.DataFrame(index=signals.index).fillna(0.0)
    old_stock = 0
    for index, row in signals.iterrows():
        day_value = backtest_data.loc[index,'Adj Close']
        if row["signal"] > 0.0:
            if current_capital >= (day_value * share_to_buy):
                portfolio.loc[index,'stock'] = share_to_buy * row["signal"] + old_stock
                old_stock = portfolio.loc[index,'stock']
                commission = (day_value * share_to_buy * commissions)
                current_capital = current_capital - (day_value * share_to_buy) - commission
                portfolio.loc[index,'cash'] = current_capital
                print("[BUY ] Date " +str(index) +" currentCap:" + str(current_capital) +" day_value: " + str(day_value) +
                       " Stock:"+ str(portfolio.loc[index,'stock']) + " Commission:" + str(commission) )
            else:
                portfolio.loc[index,'stock']  = old_stock 
                portfolio.loc[index,'cash'] = current_capital
        elif row["signal"] < 0.0:    
            if old_stock > 0:
                current_capital = current_capital + (day_value * old_stock) - (day_value * old_stock * commissions)
                old_stock = 0
                print("[SELL] Date " +str(index) +" currentCap:" + str(current_capital) +" " + " day_value: " + str(day_value) +" Stock:0" 
                      + " Commission: {0:0.2f}".format(commission))
            #else:
                #print("[SELL]")

            portfolio.loc[index,'stock']  = old_stock 
            portfolio.loc[index,'cash'] = current_capital                
        else:
            portfolio.loc[index,'stock']  = old_stock 
            portfolio.loc[index,'cash'] = current_capital           
                            
    # Add 'total' to portfolio
    portfolio['total'] = portfolio['cash'] + portfolio['stock'].multiply(backtest_data['Adj Close'], axis=0)
    portfolio['P/L %'] = ((portfolio['total']/initial_capital) - 1) *100

    return portfolio    
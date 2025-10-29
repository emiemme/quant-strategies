import pandas as pd
import importlib

def backtest_strategy(signals, backtest_data, initial_capital=10000, commissions=0.02):
    current_capital = initial_capital
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    
    for index, row in signals.iterrows():
        #print(index, row["signal"])
       print( backtest_data.loc[index,'Close'])
    positions['stock'] = 10 * signals['signal']   # Buy 100 shares on each buy signal
    # Initialize the portfolio with value owned
    portfolio = positions.multiply(backtest_data['Close'], axis=0)

    # Store the difference in shares owned
    pos_diff = positions.diff()

    # Add 'cash' to portfolio
    portfolio['cash'] = initial_capital - (pos_diff.multiply(backtest_data['Close'], axis=0)).cumsum()

    # Add 'total' to portfolio
    portfolio['total'] = portfolio['cash'] + portfolio['stock']
    portfolio['P/L %'] = ((portfolio['total']/initial_capital) - 1) *100

    return portfolio

def backtest_strategy_portfolio_sim(signals, backtest_data, symbol, initial_capital=1000, commissions=0.002, min_commission=5, print_signals= False, adj_macro_data = False, macro_data = None):
    if (not isinstance(initial_capital, (int, float))) | (initial_capital <= 0):
        raise ValueError("initial_capital must be a positive number")
    if (not isinstance(commissions, (int, float))) | (commissions < 0):
        raise ValueError("commissions must be a non-negative number")
    
    share_to_buy = 1
    current_capital = initial_capital
    portfolio = pd.DataFrame(index=signals.index).fillna(0.0)
    old_stock = 0
    for index, row in signals.iterrows():
        day_value = backtest_data[('Close', symbol)].loc[index]
        if(adj_macro_data):
            share_to_buy = adj_share_to_buy(index,macro_data,current_capital,day_value)
        if (row["signal"] > 0.0):
            if (current_capital >= (day_value * share_to_buy)):
                portfolio.loc[index,'stock'] = share_to_buy * row["signal"] + old_stock
                old_stock = portfolio.loc[index,'stock']
                commission = (day_value * share_to_buy * commissions)
                if(commission < min_commission):
                    commission = min_commission
                current_capital = current_capital - (day_value * share_to_buy) - commission
                portfolio.loc[index,'cash'] = current_capital
                if (print_signals):
                    print("[BUY ] Date " +str(index) +" currentCap:" + str(current_capital) +" day_value: " + str(day_value) +
                           " Stock:"+ str(portfolio.loc[index,'stock']) + " Commission:" + str(commission) )
            else:
                portfolio.loc[index,'stock']  = old_stock 
                portfolio.loc[index,'cash'] = current_capital
        elif (row["signal"] < 0.0):  
            if (old_stock > 0):
                commission = (day_value * old_stock * commissions)
                if(commission < min_commission):
                    commission = min_commission
                current_capital = current_capital + (day_value * old_stock) - commission
                old_stock = 0
                if print_signals:
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

    portfolio['total'] = portfolio['cash'] + (portfolio['stock'] * backtest_data[('Close', symbol)])
    portfolio['P/L %'] = ((portfolio['total']/initial_capital) - 1) *100
    portfolio['rolling_max'] = portfolio['total'].cummax()
    portfolio['drawdown'] = portfolio['total'] - portfolio['rolling_max']
    portfolio['drawdown_pct'] = portfolio['drawdown'] / portfolio['rolling_max'] * 100

    return portfolio    


def adj_share_to_buy(date,macro_data, capital, price_close):
    macrodata_t = importlib.import_module('strategies.risk_mng')
    risk_pct = macrodata_t.get_risk_for_date(date, macro_data)
    max_risk_amount = capital * risk_pct
    position_size = max_risk_amount / price_close
    return position_size
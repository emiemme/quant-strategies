
import pandas as pd

_base_risk = 0.3

def set_base_risk(base_risk):
    _base_risk = base_risk

def adjust_risk_based_on_macro(macro_data_row):
    gdp = macro_data_row['GDP']
    cpi = macro_data_row['CPI']
    unemployment = macro_data_row['Unemployment']

    risk = _base_risk  # base risk (%)

    if gdp < 0:
        risk += 0.05  # Negative PIL ➔ more risk
    if cpi > 5:
        risk += 0.05  # High inflation rate ➔ more risk
    if unemployment > 6:
        risk += 0.05  # High unemployment rate ➔ more risk

    if gdp > 3 and cpi < 2 and unemployment < 4:
        risk -= 0.05  # Strong Economy ➔ less risk

    #print("risk:" + str(risk*100) + "%")
    return max(0.005, risk)  # min risk 0.5%

def adjust_risk_based_on_macro_and_vix(macro_data_row,vix_data_row):
    gdp = macro_data_row['GDP']
    cpi = macro_data_row['CPI']
    unemployment = macro_data_row['Unemployment']

    risk = _base_risk  # base risk (%)

        # Valore VIX giornaliero
    try:
        vix = vix_data_row
    except KeyError:
        vix = 20.0  # media storica VIX

    if gdp < 0:
        risk += 0.05  # Negative PIL ➔ more risk
    if cpi > 5:
        risk += 0.05  # High inflation rate ➔ more risk
    if unemployment > 6:
        risk += 0.05  # High unemployment rate ➔ more risk

    if gdp > 3 and cpi < 2 and unemployment < 4:
        risk -= 0.05  # Strong Economy ➔ less risk

    # Adjust col VIX
    if vix > 25:
        risk_pct *= 0.5  # volatilità alta = riduci rischio
    elif vix < 15:
        risk_pct *= 1.2  # volatilità bassa = puoi rischiare di più

    #print("risk:" + str(risk*100) + "%")
    return max(0.005, risk)  # min risk 0.5%

def get_risk_for_date(current_date, macro_data):
    available_data = macro_data[macro_data.index <= current_date]
    #print(macro_data.tail())
    if available_data.empty:
        return 0.02  # Default no data

    latest_macro = available_data.iloc[-1]
    return adjust_risk_based_on_macro(latest_macro)
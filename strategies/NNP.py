import pandas as pd
import yfinance as yf
import numpy as np

from keras.models import Sequential
from keras.layers import LSTM, GRU, Dropout, Dense
from sklearn.preprocessing import MinMaxScaler
import keras

from datetime import datetime, timedelta

from matplotlib.dates import MonthLocator, DateFormatter
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os.path


def download_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    stock_data['MACD'] = stock_data['Close'].ewm(span=12, adjust=False).mean() - stock_data['Close'].ewm(span=26, adjust=False).mean()
    stock_data['RSI'] = compute_RSI(stock_data['Close'])
    stock_data['Volume'] = stock_data['Volume']
    return stock_data

def compute_RSI(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])
    return np.array(X), np.array(y)

def normalize_data(stock_data):
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(stock_data[['Close', 'MACD', 'RSI', 'Volume']].dropna())

    train_size = int(len(scaled_data) * 0.8)
    train_data, test_data = scaled_data[:train_size], scaled_data[train_size:]
    
    seq_length=60
    X_train, y_train = create_sequences(train_data,seq_length)
    X_test, y_test = create_sequences(test_data,seq_length)
    
    return X_train, y_train, X_test, y_test, scaler

def model_training_LSTM(X_train, y_train):    
    model = Sequential()
    #Adding the first LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 100, return_sequences = True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))

    # Adding a second LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 100, return_sequences = False))
    model.add(Dropout(0.2))

    # Adding the output layer
    model.add(Dense(units = 50))
    model.add(Dense(units = 1))

    model.compile(optimizer='adam',loss='mean_squared_error')
    # train the model
    model.fit(X_train, y_train, epochs=100, batch_size=32)
    return model

def model_training_GRU(X_train, Y_train):
    gru_model = Sequential()
    # First GRU layer with dropout
    gru_model.add(GRU(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    gru_model.add(Dropout(0.2))

    # Second GRU layer with dropout
    gru_model.add(GRU(50, return_sequences=True))
    gru_model.add(Dropout(0.2))

    # Third GRU layer with dropout
    gru_model.add(GRU(50, return_sequences=True))
    gru_model.add(Dropout(0.2))

    # Fourth GRU layer with dropout
    gru_model.add(GRU(50))
    gru_model.add(Dropout(0.2))

    # Output layer
    gru_model.add(Dense(1))

    gru_model.compile(optimizer='adam', loss='mean_squared_error')
    # train the model
    gru_model.fit(X_train, Y_train, epochs=100, batch_size=32)
    return gru_model

def model_generate_prediction(model, X_test, y_test, scaler):
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(np.hstack((predictions, np.zeros((len(predictions), 3)))))[:, 0]
    
    future_input = X_test[-1]
    future_predictions = []
    for _ in range(30):
        future_pred = model.predict(future_input.reshape(1, future_input.shape[0], future_input.shape[1]))
        future_predictions.append(future_pred[0,0])
        future_input = np.roll(future_input, -1, axis=0)
        future_input[-1, 0] = future_pred
    
    return predictions, future_predictions

def model_evaluation(model, X_test, Y_test):   
    # evaluate the model
    test_loss = model.evaluate(X_test, Y_test)
    print('Test Loss:', test_loss)   


def plot_data(symbol, y_train, y_test, future_predictions, forecast, scaler):
    y_train_real = scaler.inverse_transform(np.hstack((y_train.reshape(-1,1), np.zeros((len(y_train), 3)))))[:, 0]
    y_test_real = scaler.inverse_transform(np.hstack((y_test.reshape(-1,1), np.zeros((len(y_test), 3)))))[:, 0]
    forecast_real = scaler.inverse_transform(np.hstack((np.array(forecast).reshape(-1,1), np.zeros((len(forecast), 3)))))[:, 0]

    plt.figure(figsize=(14,5))
    #plt.plot(range(len(y_train_real)), y_train_real, label='Train Data')
    plt.plot(range(len(y_train_real), len(y_train_real) + len(y_test_real)), y_test_real, label='Actual Prices')
    plt.plot(range(len(y_train_real), len(y_train_real) + len(y_test_real)), future_predictions, label='Predicted Prices')
    plt.plot(range(len(y_train_real) + len(y_test_real), len(y_train_real) + len(y_test_real) + len(forecast_real)), forecast_real, label='Forecast', linestyle='dotted')

    plt.legend()
    if not  os.path.exists('img'):
        os.mkdir('img')
    imgPath = 'img/' + symbol + '/'
    isExist = os.path.exists(imgPath)
    if not isExist:
        os.mkdir(imgPath)
    currentDateTime = datetime.now()
    currentDateTime_string = currentDateTime.strftime("%d_%m_%YT%H_%M_%S")
    plt.savefig('img/' + symbol + '/' + str(currentDateTime_string) + '_neural_network_pattern.png')
    plt.show()

def get_signals(symbol, start_date, end_date, use_model="LSTM"):
    stock_data = download_stock_data(symbol, start_date, end_date)
    X_train, y_train, X_test, y_test, scaler = normalize_data(stock_data)

    if not  os.path.exists('models'):
        os.mkdir('models')

    modelsPath = 'models/' + symbol + '/'
    isExist = os.path.exists(modelsPath)
    if not isExist:
        os.mkdir(modelsPath)
    if use_model == "LSTM":        
        if not os.path.exists(modelsPath + symbol + "_nnp_LSTM.keras"):
            model = model_training_LSTM(X_train, y_train)
            model.save(modelsPath + symbol + "_nnp_LSTM.keras")
        else:
            model = keras.models.load_model(modelsPath + symbol + "_nnp_LSTM.keras")
    elif use_model == "GRU":          
        if not os.path.exists(modelsPath + symbol + "_nnp_GRU.keras"):
            model = model_training_GRU(X_train, y_train)
            model.save(modelsPath + symbol + "_nnp_GRU.keras")
        else:
            model = keras.models.load_model(modelsPath + symbol + "_nnp_GRU.keras")    
    
    model_evaluation(model, X_test, y_test)
    future_predictions, forecast = model_generate_prediction(model, X_test, y_test, scaler)
 
    plot_data(symbol, y_train,  y_test, future_predictions, forecast, scaler)

    future_reg = (forecast[-1] - forecast[0])

    return future_reg


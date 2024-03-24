import pandas as pd
import yfinance as yf
import numpy as np

from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense
from sklearn.preprocessing import MinMaxScaler
import keras

from datetime import datetime, timedelta

from matplotlib.dates import MonthLocator, DateFormatter
import matplotlib.pyplot as plt

import os.path


def download_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return stock_data

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data['Close'][i:i+seq_length])
        y.append(data['Close'][i+seq_length])
    return np.array(X), np.array(y)

def normalize_data(stock_data):
    # normalize data
    df = pd.DataFrame(index=stock_data.index)
    df['Close'] = stock_data['Close']
    scaler = MinMaxScaler()
    df['Close'] = scaler.fit_transform(df['Close'].values.reshape(-1, 1))

    # split data into training and testing sets
    train_data = df[:int(len(df)*0.8)]
    test_data = df[int(len(df)*0.8):]

    seq_length = 30 #10  # Define the sequence length (number of past days to consider)
    X_train, Y_train = create_sequences(train_data, seq_length)
    X_test, Y_test = create_sequences(test_data, seq_length)

    # Reshape input for LSTM (samples, timesteps, features)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    return X_train, Y_train, X_test, Y_test, scaler

def model_training(X_train, Y_train):    
    model = Sequential()
    #Adding the first LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 100, return_sequences = True, input_shape = (X_train.shape[1], 1)))
    model.add(Dropout(0.2))

    # Adding a second LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 100, return_sequences = True))
    model.add(Dropout(0.2))

    # Adding a third LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 100, return_sequences = True))
    model.add(Dropout(0.2))

    # Adding a fourth LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 100))
    model.add(Dropout(0.2))

    # Adding the output layer
    model.add(Dense(units = 25))
    model.add(Dense(units = 1))

    model.compile(optimizer='adam',loss='mean_squared_error')
    # train the model
    model.fit(X_train, Y_train, epochs=100, batch_size=32)
    return model

def model_generate_prediction(model, X_test, scaler, stock_data):
    # make predictions
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    df_prediction=pd.DataFrame(predictions, columns=['predictions'],index=stock_data[int(len(stock_data) - len(predictions)):].index  )

    df = pd.DataFrame(index=stock_data.index)
    df['Close'] = stock_data['Close']
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df['Close'].values.reshape(-1, 1))
    # Predict the next 10 days
    last_60_days = scaled_data[-60:]
    next_10_days = []
    for i in range(30):
        X_ntest = np.array([last_60_days])
        X_ntest = np.reshape(X_ntest, (X_ntest.shape[0], X_ntest.shape[1], 1))
        pred_price = model.predict(X_ntest)
        pred_price_unscaled = scaler.inverse_transform(pred_price)
        next_10_days.append(pred_price_unscaled[0, 0])
        last_60_days = np.append(last_60_days, pred_price, axis=0)[-60:]

    # Create a dataframe for the next 10 days
    last_date = stock_data.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    future_predictions = pd.DataFrame(data={'Date': future_dates, 'Close': next_10_days})
    future_predictions.set_index('Date', inplace=True)  
    
    return df_prediction,future_predictions

def model_evaluation(model, X_test, Y_test):   
    # evaluate the model
    test_loss = model.evaluate(X_test, Y_test)
    print('Test Loss:', test_loss)   

def get_signals(symbol, start_date, end_date):
    stock_data = download_stock_data(symbol, start_date, end_date)
    X_train, y_train, X_test, y_test, scaler = normalize_data(stock_data)        

    if not  os.path.exists('models'):
        os.mkdir('models')

    modelsPath = 'models/' + symbol + '/'
    isExist = os.path.exists(modelsPath)
    if not isExist:
        os.mkdir(modelsPath)
    if not os.path.exists(modelsPath + symbol + "_nnp.keras"):
        model = model_training(X_train, y_train)
        model.save(modelsPath + symbol + "_nnp.keras")
    else:
        model = keras.models.load_model(modelsPath + symbol + "_nnp.keras")
    
    model_evaluation(model, X_test, y_test)
    predictions, future_predictions = model_generate_prediction(model, X_test,scaler, stock_data)

    plt.plot(stock_data['Close'][int(len(stock_data)*0.8):], color = 'blue')
    plt.plot(future_predictions, color = 'red')
    plt.plot(predictions, color = 'green')
    plt.xticks(rotation=90)

    plt.ylabel(symbol + ' Stock Price')
    if not  os.path.exists('img'):
        os.mkdir('img')
    imgPath = 'img/' + symbol + '/'
    isExist = os.path.exists(imgPath)
    if not isExist:
        os.mkdir(imgPath)
    currentDateTime = datetime.now()
    currentDateTime_string = currentDateTime.strftime("%d_%m_%YT%H_%M_%S")
    plt.savefig('img/' + symbol + '/' + str(currentDateTime_string) + '_neural_network_pattern.png')


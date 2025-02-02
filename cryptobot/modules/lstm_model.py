import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import numpy as np
import tf2onnx
import os
import logging
import pandas as pd

def build_lstm_model(input_shape, units=50, dropout_rate=0.2):
    model = Sequential()
    model.add(LSTM(units, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(dropout_rate))
    model.add(LSTM(units))
    model.add(Dropout(dropout_rate))
    model.add(Dense(1, activation='linear'))
    model.compile(optimizer='adam', loss='mse')
    return model

def train_lstm_model(historical_data: pd.DataFrame, epochs=10, batch_size=16):
    """
    Trénuje LSTM model na historických datech. Používá sloupec 'close'.
    Vrací cestu k uloženému ONNX modelu.
    """
    data = historical_data['close'].values.reshape(-1, 1)
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    sequence_length = 10
    X, y = [], []
    for i in range(len(scaled_data) - sequence_length):
        X.append(scaled_data[i:i+sequence_length])
        y.append(scaled_data[i+sequence_length])
    X, y = np.array(X), np.array(y)
    
    input_shape = (X.shape[1], X.shape[2])
    model = build_lstm_model(input_shape)
    
    logging.info("Training LSTM model...")
    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
    
    saved_model_path = "lstm_saved_model"
    model.save(saved_model_path, save_format="tf")
    
    onnx_model_path = "trained_lstm.onnx"
    spec = (tf.TensorSpec((None, X.shape[1], X.shape[2]), tf.float32, name="input"),)
    tf2onnx.convert.from_keras(model, input_signature=spec, output_path=onnx_model_path)
    
    logging.info("LSTM model trained and converted to ONNX at %s", onnx_model_path)
    return onnx_model_path

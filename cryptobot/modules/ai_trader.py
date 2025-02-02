import onnxruntime as ort
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging
from modules import lstm_model

class AITrader:
    def __init__(self, model_path: str):
        providers = ort.get_available_providers()
        sess_options = ort.SessionOptions()
        # Nastavení optimalizace (případně lze přidat další C++ extension optimalizace)
        sess_options.optimized_model_filepath = "optimized_model.onnx"
        if "CUDAExecutionProvider" in providers:
            self.model = ort.InferenceSession(model_path, sess_options, providers=["CUDAExecutionProvider"])
        else:
            self.model = ort.InferenceSession(model_path, sess_options, providers=["CPUExecutionProvider"])
        self.scaler = MinMaxScaler()
    
    def predict(self, data: np.array) -> np.array:
        normalized_data = self.scaler.fit_transform(data)
        prediction = self.model.run(None, {"input": normalized_data.astype(np.float32)})
        return prediction
    
    def predict_lot_size(self, data: np.array) -> float:
        # Příklad: použijte predikci modelu k určení optimální velikosti pozice
        prediction = self.predict(data)
        lot_size = float(prediction[0][0])
        return lot_size

    def offline_training(self, historical_data):
        logging.info("Starting offline training using LSTM model...")
        trained_model_path = lstm_model.train_lstm_model(historical_data)
        self.model = ort.InferenceSession(trained_model_path)
        logging.info("Offline training completed and model reloaded.")
        return True
    
    def retrain_model(self, new_data):
        logging.info("Retraining model with new data using LSTM architecture...")
        trained_model_path = lstm_model.train_lstm_model(new_data)
        self.model = ort.InferenceSession(trained_model_path)
        logging.info("Retraining completed and new model loaded.")
        return True

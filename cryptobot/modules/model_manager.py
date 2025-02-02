import logging
import pandas as pd

class ModelManager:
    def __init__(self):
        self.models = {}
    
    def load_model(self, name: str, model_path: str):
        self.models[name] = model_path
        logging.info(f"Model {name} loaded from {model_path}")
    
    def get_model(self, name: str):
        return self.models.get(name)
    
    def update_model(self, name: str, new_data: pd.DataFrame):
        logging.info(f"Updating model {name} with new data.")
        # Zde můžete vyvolat retraining či aktualizaci modelu
        return True

import unittest
import pandas as pd
import numpy as np
from modules.data_processor import DataProcessor

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.dp = DataProcessor()
        dates = pd.date_range(end=pd.Timestamp.now(), periods=20, freq="T")
        self.data = pd.DataFrame({
            "high": np.random.uniform(50000, 51000, size=20),
            "low": np.random.uniform(49000, 50000, size=20),
            "close": np.random.uniform(49500, 50500, size=20)
        }, index=dates)
    
    def test_atr_calculation(self):
        atr = self.dp.calculate_atr(self.data)
        self.assertFalse(atr.isnull().all())

if __name__ == '__main__':
    unittest.main()

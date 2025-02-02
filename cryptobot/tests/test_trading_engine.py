import unittest
import asyncio
from modules.api_manager import APIManager
from modules.data_processor import DataProcessor
from modules.ai_trader import AITrader
from modules.trading_engine import TradingEngine

class TestTradingEngine(unittest.TestCase):
    def setUp(self):
        self.api_manager = APIManager("DUMMY_KEY", "DUMMY_SECRET")
        self.dp = DataProcessor()
        self.ai_trader = AITrader("model.onnx")
        self.engine = TradingEngine(self.api_manager, self.dp, self.ai_trader)
    
    def test_execute_trade(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        order = loop.run_until_complete(self.engine.execute_long_trade())
        self.assertEqual(order.get("status"), "simulated")
    
    def test_execute_short_trade(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        order = loop.run_until_complete(self.engine.execute_short_trade())
        self.assertEqual(order.get("status"), "simulated")

if __name__ == '__main__':
    unittest.main()

import asyncio
import logging
from modules.api_manager import APIManager
from modules.data_processor import DataProcessor
from modules.ai_trader import AITrader
from modules.trading_engine import TradingEngine
from modules.model_manager import ModelManager
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY", "DUMMY_API_KEY")
API_SECRET = os.getenv("API_SECRET", "DUMMY_API_SECRET")

async def main():
    logging.basicConfig(level=logging.INFO)
    # Připojení s automatickými reconnecty
    api_manager = APIManager(API_KEY, API_SECRET)
    await api_manager.connect_with_retry()
    
    dp = DataProcessor()
    ai_trader = AITrader("model.onnx")
    trading_engine = TradingEngine(api_manager, dp, ai_trader)
    
    # Příklad spuštění obchodní smyčky v manuálním režimu s hedge podporou
    trading_engine.mode = "manual"
    trading_engine.hedge_mode = True  # aktivace hedge strategie
    trading_engine.symbol = "BTCUSDT"
    await trading_engine.trade_loop()

if __name__ == "__main__":
    asyncio.run(main())

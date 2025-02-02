import asyncio
import streamlit as st
import pandas as pd
from modules.api_manager import APIManager
from modules.data_processor import DataProcessor
from modules.ai_trader import AITrader
from modules.trading_engine import TradingEngine
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY", "DUMMY_API_KEY")
API_SECRET = os.getenv("API_SECRET", "DUMMY_API_SECRET")

def run_gui():
    st.title("CryptoBot - Binance Trading")
    
    api_manager = APIManager(API_KEY, API_SECRET)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(api_manager.connect_with_retry())
    
    exchange_info = loop.run_until_complete(api_manager.get_exchange_info())
    available_pairs = [s['symbol'] for s in exchange_info['symbols'] if s.get('status') == 'TRADING']
    symbol = st.selectbox("Select Trading Pair", available_pairs)
    
    dp = DataProcessor()
    ai_trader = AITrader("model.onnx")
    trading_engine = TradingEngine(api_manager, dp, ai_trader)
    trading_engine.symbol = symbol
    
    account_balance = loop.run_until_complete(api_manager.get_account_balance())
    st.write("Account Balance:", account_balance)
    
    mode = st.selectbox("Select Trading Mode", ["manual", "ai"])
    trading_engine.mode = mode
    # Možnost volby režimu lot sizingu: manual, ATR nebo AI
    lot_sizing_mode = st.selectbox("Lot Sizing Mode", ["manual", "ATR", "AI"])
    trading_engine.lot_sizing_mode = lot_sizing_mode
    manual_lot = st.number_input("Manual Lot Size", value=trading_engine.lot_size, step=0.001)
    trading_engine.manual_lot_size = manual_lot
    leverage = st.number_input("Leverage", value=trading_engine.leverage, step=1)
    trading_engine.leverage = leverage
    # Možnost nastavení SL a TP
    stop_loss = st.number_input("Stop Loss (%)", value=2.0, step=0.1)
    take_profit = st.number_input("Take Profit (%)", value=4.0, step=0.1)
    trading_engine.fixed_stop_loss = stop_loss / 100.0
    trading_engine.fixed_take_profit = take_profit / 100.0
    
    if st.button("Start Trading"):
        st.success(f"Trading started for {symbol} in {mode} mode")
        loop.create_task(trading_engine.trade_loop())
    
    if st.button("Stop Trading"):
        loop.run_until_complete(trading_engine.stop_trading())
        st.info("Trading stopped.")
    
    if trading_engine.price_history:
        data_chart = pd.DataFrame({
            "Price": list(trading_engine.price_history),
            "Prediction": list(trading_engine.prediction_history) if trading_engine.prediction_history else [0]*len(trading_engine.price_history)
        })
        st.line_chart(data_chart)
    
    st.write("API Metrics:", api_manager.api_metrics)

if __name__ == "__main__":
    run_gui()

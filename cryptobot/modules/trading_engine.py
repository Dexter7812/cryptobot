import asyncio
import logging
import time
import gc
import numpy as np
import pandas as pd
import psutil
from collections import deque

class TradingEngine:
    def __init__(self, api_manager, data_processor, ai_trader):
        self.api_manager = api_manager
        self.data_processor = data_processor
        self.ai_trader = ai_trader
        
        # Obchodní režimy
        self.mode = "manual"  # "manual" nebo "ai"
        self.lot_sizing_mode = "ATR"  # "manual", "ATR" nebo "AI"
        self.manual_lot_size = 0.001
        
        # Parametry obchodování
        self.lot_size = 0.001
        self.leverage = 10
        self.symbol = "BTCUSDT"
        self.fixed_stop_loss = None  # pokud nastaveno, slouží jako fixní SL (v procentech)
        self.fixed_take_profit = None  # pokud nastaveno, slouží jako fixní TP (v procentech)
        
        # Hedge strategie
        self.hedge_mode = False
        
        # Parametry trailing stop / break-even
        self.trail_stop = None
        self.break_even_threshold = 1.02
        
        # Dynamická frekvence aktualizací
        self.dynamic_sleep_time = 5
        
        # Circular buffers pro historická data (maximálně 1000 záznamů)
        self.price_history = deque(maxlen=1000)
        self.prediction_history = deque(maxlen=1000)
        self.order_history = deque(maxlen=1000)
        self.alerts = deque(maxlen=1000)
        
        # Performance metriky pro retraining
        self.model_performance = []
    
    async def update_trading_parameters(self):
        # Získání dummy historických dat (v praxi získávejte reálná data)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq="T")
        dummy_data = pd.DataFrame({
            "high": np.random.uniform(50000, 51000, size=30),
            "low": np.random.uniform(49000, 50000, size=30),
            "close": np.random.uniform(49500, 50500, size=30)
        }, index=dates)
        atr_series = self.data_processor.calculate_atr(dummy_data)
        current_atr = atr_series.iloc[-1] if not atr_series.empty else 0
        volatility = self.data_processor.calculate_volatility(dummy_data['close'])
        
        # Dynamické nastavení lot size – podle zvoleného režimu
        if self.lot_sizing_mode == "manual":
            self.lot_size = self.manual_lot_size
        elif self.lot_sizing_mode == "ATR":
            self.lot_size = 0.002 if current_atr > 50 else 0.001
        elif self.lot_sizing_mode == "AI":
            # Použijte AI predikci pro optimální lot size
            sample_data = np.random.rand(1, 10)
            self.lot_size = self.ai_trader.predict_lot_size(sample_data)
        
        # Dynamická úprava páky
        self.leverage = 20 if volatility > 0.01 else 10
        
        # Adaptivní frekvence aktualizací
        self.dynamic_sleep_time = 2 if volatility > 0.01 else 5
        
        # Adaptivní trailing stop-loss: vzdálenost = ATR * koeficient (např. 1.5)
        self.adaptive_trail_stop_distance = current_atr * 1.5 if current_atr else None
        
        logging.info(f"Parameters updated: lot_size={self.lot_size}, leverage={self.leverage}, sleep_time={self.dynamic_sleep_time}")
    
    async def update_stop_loss(self, order_id, new_stop_loss):
        # Placeholder: zde by se zavolalo API pro úpravu aktivní objednávky
        logging.info(f"Updating stop loss for order {order_id} to {new_stop_loss}")
        # Simulovaná odpověď:
        return {"order_id": order_id, "new_stop_loss": new_stop_loss, "status": "updated"}
    
    async def execute_trade(self, side: str, is_short: bool = False):
        await self.update_trading_parameters()
        order_side = side
        if is_short:
            order_side = "SELL" if side == "BUY" else "BUY"
        order = await self.api_manager.place_order(
            symbol=self.symbol,
            side=order_side,
            amount=self.lot_size,
            order_type="MARKET",
            is_futures=True
        )
        self.order_history.append(order)
        msg = f"Trade executed: {order}"
        self.alerts.append(msg)
        logging.info(msg)
        return order
    
    async def execute_long_trade(self):
        return await self.execute_trade("BUY", is_short=False)
    
    async def execute_short_trade(self):
        return await self.execute_trade("SELL", is_short=True)
    
    async def apply_trailing_stop(self, entry_price: float, current_price: float):
        # Adaptivní trailing stop-loss založený na aktuální ceně a ATR
        if self.adaptive_trail_stop_distance:
            proposed_stop = current_price - self.adaptive_trail_stop_distance
        else:
            proposed_stop = current_price * 0.98  # výchozí hodnota
        if not self.trail_stop or proposed_stop > self.trail_stop:
            self.trail_stop = proposed_stop
            logging.info(f"Trailing stop updated to: {self.trail_stop}")
    
    async def check_break_even(self, entry_price: float, current_price: float):
        if current_price >= entry_price * self.break_even_threshold:
            logging.info("Break-even threshold reached, adjusting stop loss to break-even.")
            # Aktualizace stop loss pomocí API – zde simulujeme update
            await self.update_stop_loss(order_id="dummy_order", new_stop_loss=entry_price)
    
    async def monitor_model_performance(self):
        # Simulovaná metrika – v praxi by se měřila úspěšnost obchodů, MSE predikcí apod.
        performance = np.random.rand()
        self.model_performance.append(performance)
        logging.info(f"Current model performance: {performance}")
        # Pokud průměrná performance klesne pod prahovou hodnotu, spustit retraining
        if len(self.model_performance) >= 10 and np.mean(self.model_performance[-10:]) < 0.5:
            logging.info("Performance threshold exceeded, initiating retraining.")
            # V reálném nasazení předat reálná data
            await self.ai_trader.retrain_model(new_data=pd.DataFrame({"close": np.random.rand(100)}))
    
    async def trade_loop(self):
        self.running = True
        try:
            entry_price = await self.api_manager.get_market_price(self.symbol)
        except Exception as e:
            logging.error("Failed to get entry price: %s", e)
            return
        logging.info(f"Entry price: {entry_price}")
        while self.running:
            try:
                current_price = await self.api_manager.get_market_price(self.symbol)
                self.price_history.append(current_price)
                logging.info(f"Current price: {current_price}")
                
                await self.apply_trailing_stop(entry_price, current_price)
                await self.check_break_even(entry_price, current_price)
                
                # Detekce abnormalit v order booku
                await self.api_manager.detect_order_book_abnormalities(self.symbol)
                # Monitor síťového provozu
                self.api_manager.monitor_network()
                
                if self.mode == "ai":
                    dummy_input = np.random.rand(1, 10)
                    prediction = self.ai_trader.predict(dummy_input)
                    pred_value = prediction[0][0] if prediction and prediction[0].size > 0 else 0
                    self.prediction_history.append(pred_value)
                    logging.info(f"AI prediction: {prediction}")
                    if self.hedge_mode:
                        # Příklad: pokud je predikce výrazně nad 0.55, otevíráme long, pod 0.45 otevíráme short,
                        # v mezích držíme obě pozice (simulace)
                        if pred_value > 0.55:
                            await self.execute_long_trade()
                        elif pred_value < 0.45:
                            await self.execute_short_trade()
                        else:
                            logging.info("Hedge mode active: maintaining balanced positions.")
                    else:
                        if pred_value > 0.5:
                            await self.execute_long_trade()
                        else:
                            await self.execute_short_trade()
                else:
                    # Manuální režim – očekává se vstup od operátora přes GUI
                    pass
                
                # Batch processing pro více párů lze implementovat zde (příklad: načíst ceny pro více symbolů)
                # prices = await self.api_manager.get_multiple_market_prices(["BTCUSDT", "ETHUSDT"])
                # logging.info(f"Batch prices: {prices}")
                
                # Monitorování modelu pro auto-retraining
                await self.monitor_model_performance()
                
                # Profilování paměti
                mem = psutil.virtual_memory()
                logging.info("Memory Usage: %.2f%%", mem.percent)
                
                gc.collect()
                await asyncio.sleep(self.dynamic_sleep_time)
            except asyncio.CancelledError:
                logging.info("Trade loop cancelled.")
                break
            except Exception as e:
                logging.error("Error in trade loop: %s", e)
        logging.info("Exiting trade loop.")
    
    async def stop_trading(self):
        self.running = False
        logging.info("Trading stopped.")

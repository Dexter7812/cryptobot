import asyncio
import time
import logging
from functools import lru_cache
from typing import Optional, Dict, List
from binance import AsyncClient
import psutil
from .exceptions import APIConnectionError

class APIManager:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client: Optional[AsyncClient] = None
        self.api_metrics = {"requests": 0, "latency": [], "rate_limit_triggered": 0}
    
    async def connect(self):
        try:
            self.client = await AsyncClient.create(self.api_key, self.api_secret)
            logging.info("API connected successfully.")
        except Exception as e:
            logging.error("API connection failed: %s", e)
            self.client = None
            raise APIConnectionError("Nepodařilo se připojit k API.")
        return self.client

    async def connect_with_retry(self, retries: int = 5, delay: int = 5):
        for attempt in range(retries):
            try:
                if await self.connect():
                    return self.client
            except APIConnectionError:
                logging.info("Reconnect attempt %d/%d", attempt+1, retries)
                await asyncio.sleep(delay)
        logging.error("All reconnect attempts failed, switching to simulation mode.")
        return None

    @lru_cache(maxsize=1)
    async def get_exchange_info(self) -> Dict:
        if self.client:
            try:
                start = time.time()
                info = await self.client.get_exchange_info()
                self.api_metrics["requests"] += 1
                self.api_metrics["latency"].append(time.time() - start)
                return info
            except Exception as e:
                logging.error("Error getting exchange info: %s", e)
        logging.warning("Using simulated exchange info.")
        return {"symbols": [{"symbol": "BTCUSDT", "status": "TRADING"},
                            {"symbol": "ETHUSDT", "status": "TRADING"}]}
    
    async def get_account_balance(self) -> Dict[str, float]:
        if self.client:
            try:
                start = time.time()
                account_info = await self.client.get_account()
                self.api_metrics["requests"] += 1
                self.api_metrics["latency"].append(time.time() - start)
                balances = {asset['asset']: float(asset['free']) for asset in account_info['balances']}
                return balances
            except Exception as e:
                logging.error("Error fetching account balance: %s", e)
        logging.warning("Using simulated account balance.")
        return {"BTC": 0.0, "USDT": 1000.0}
    
    async def get_market_price(self, symbol: str) -> float:
        if self.client:
            try:
                start = time.time()
                ticker = await self.client.get_symbol_ticker(symbol=symbol)
                self.api_metrics["requests"] += 1
                self.api_metrics["latency"].append(time.time() - start)
                return float(ticker['price'])
            except Exception as e:
                logging.error("Error fetching market price: %s", e)
        logging.warning("Using simulated market price.")
        return 50000.0
    
    async def get_multiple_market_prices(self, symbols: List[str]) -> Dict[str, float]:
        prices = {}
        for sym in symbols:
            prices[sym] = await self.get_market_price(sym)
        return prices
    
    async def place_order(self, symbol: str, side: str, amount: float, order_type="MARKET", is_futures=False) -> Dict:
        if self.client:
            try:
                start = time.time()
                if is_futures:
                    order = await self.client.futures_create_order(
                        symbol=symbol, side=side, type=order_type, quantity=amount
                    )
                else:
                    order = await self.client.create_order(
                        symbol=symbol, side=side, type=order_type, quantity=amount
                    )
                self.api_metrics["requests"] += 1
                self.api_metrics["latency"].append(time.time() - start)
                return order
            except Exception as e:
                logging.error("Order execution failed: %s", e)
        logging.warning("Simulated order executed.")
        return {"symbol": symbol, "side": side, "amount": amount, "status": "simulated"}
    
    async def get_position_risk(self, symbol: str) -> Dict:
        if self.client:
            try:
                start = time.time()
                risk_info = await self.client.futures_position_risk(symbol=symbol)
                self.api_metrics["requests"] += 1
                self.api_metrics["latency"].append(time.time() - start)
                return risk_info
            except Exception as e:
                logging.error("Error fetching position risk: %s", e)
        logging.warning("Using simulated position risk.")
        return {"symbol": symbol, "positionRisk": "simulated"}
    
    async def get_order_book_depth(self, symbol: str) -> Dict:
        if self.client:
            try:
                start = time.time()
                depth = await self.client.get_order_book(symbol=symbol)
                self.api_metrics["requests"] += 1
                self.api_metrics["latency"].append(time.time() - start)
                return depth
            except Exception as e:
                logging.error("Error fetching order book depth: %s", e)
        logging.warning("Using simulated order book depth.")
        return {"bids": [], "asks": []}

    async def detect_order_book_abnormalities(self, symbol: str, spread_threshold: float = 0.002) -> None:
        depth = await self.get_order_book_depth(symbol)
        if depth["bids"] and depth["asks"]:
            best_bid = float(depth["bids"][0][0])
            best_ask = float(depth["asks"][0][0])
            mid_price = (best_bid + best_ask) / 2
            spread = (best_ask - best_bid) / mid_price
            if spread > spread_threshold:
                logging.warning("Abnormal spread detected for %s: %.4f", symbol, spread)
    
    def monitor_network(self) -> None:
        net_io = psutil.net_io_counters()
        logging.info("Network - Bytes Sent: %d, Bytes Recv: %d", net_io.bytes_sent, net_io.bytes_recv)
    
    async def close(self):
        if self.client:
            await self.client.close_connection()
        self.api_key = None
        self.api_secret = None

# core/bitget_client.py - Enhanced with CCXT integration
import os
import time
import ccxt
import asyncio
from typing import Dict, List, Optional, Any
from config.settings import ExchangeConfig
from utils.telegram_logger import send_telegram_log

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("📝 python-dotenv not available, using config values")

class BitgetClient:
    def __init__(self):
        """Initialize Bitget client with CCXT integration."""
        # Try environment variables first, fallback to config
        self.api_key = os.getenv('BITGET_API_KEY', ExchangeConfig.BITGET_API_KEY)
        self.api_secret = os.getenv('BITGET_API_SECRET', ExchangeConfig.BITGET_API_SECRET)
        self.api_passphrase = os.getenv('BITGET_API_PASSPHRASE', ExchangeConfig.BITGET_API_PASSPHRASE)
        self.sandbox = os.getenv('BITGET_SANDBOX', 'true').lower() == 'true'
        self.enable_live_trading = os.getenv('ENABLE_LIVE_TRADING', 'false').lower() == 'true'
        
        try:
            # Check if we have valid API credentials
            has_credentials = (
                self.api_key and 
                self.api_key != "your_api_key_here" and
                self.api_secret and 
                self.api_secret != "your_api_secret_here"
            )
            
            if has_credentials:
                # Initialize CCXT Bitget client
                self.exchange = ccxt.bitget({
                    'apiKey': self.api_key,
                    'secret': self.api_secret,
                    'password': self.api_passphrase,
                    'sandbox': self.sandbox,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'swap',  # For futures trading
                    }
                })
                
                if self.enable_live_trading:
                    print("🔗 Live Bitget client initialized via CCXT")
                    print(f"📊 Sandbox mode: {self.sandbox}")
                else:
                    print("📡 Bitget client ready (set ENABLE_LIVE_TRADING=true for live trading)")
            else:
                print("📡 Mock Bitget client initialized (add API keys for live trading)")
                self.exchange = None
                
        except Exception as e:
            print(f"⚠️ Failed to initialize Bitget client: {e}")
            print("📡 Falling back to mock client")
            self.exchange = None

    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        if not self.exchange or not self.enable_live_trading:
            # Mock implementation
            return {"USDT": {"free": 1000.0, "used": 0.0, "total": 1000.0}}
        
        try:
            balance = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.fetch_balance
            )
            return balance
        except Exception as e:
            await send_telegram_log(f"❌ Error fetching balance: {e}", tag="error")
            return {"error": str(e)}

    async def get_positions(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get open positions."""
        if not self.exchange or not self.enable_live_trading:
            # Mock implementation
            return []
        
        try:
            if symbol:
                positions = await asyncio.get_event_loop().run_in_executor(
                    None, self.exchange.fetch_positions, [symbol]
                )
            else:
                positions = await asyncio.get_event_loop().run_in_executor(
                    None, self.exchange.fetch_positions
                )
            return [pos for pos in positions if pos['contracts'] > 0]
        except Exception as e:
            await send_telegram_log(f"❌ Error fetching positions: {e}", tag="error")
            return []

    async def place_order(self, symbol: str, side: str, amount: float, 
                         price: float = None, order_type: str = "market",
                         reduce_only: bool = False) -> Dict[str, Any]:
        """Place an order."""
        if not self.exchange or not self.enable_live_trading:
            # Mock implementation
            print(f"📤 Mock order: {side} {amount} {symbol} @ {price or 'market'}")
            await send_telegram_log(f"📤 Mock Order: {side} {amount} {symbol} @ {price or 'market'}")
            return {
                "order_id": f"bitget_mock_{int(time.time())}",
                "symbol": symbol,
                "side": side.lower(),
                "amount": amount,
                "price": price,
                "type": order_type,
                "status": "filled"
            }
        
        try:
            # Prepare order parameters
            params = {}
            if reduce_only:
                params['reduceOnly'] = True
                
            # Place order via CCXT
            order = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.exchange.create_order(
                    symbol, order_type, side.lower(), amount, price, params
                )
            )
            
            await send_telegram_log(
                f"✅ Order placed: {side} {amount} {symbol} @ {price or 'market'} | ID: {order['id']}"
            )
            return order
            
        except Exception as e:
            error_msg = f"❌ Order failed: {side} {amount} {symbol} - {e}"
            await send_telegram_log(error_msg, tag="error")
            return {"error": str(e)}

    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an order."""
        if not self.exchange or not self.enable_live_trading:
            print(f"❌ Mock cancel order: {order_id}")
            return {"order_id": order_id, "status": "cancelled"}
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.cancel_order, order_id, symbol
            )
            await send_telegram_log(f"❌ Order cancelled: {order_id}")
            return result
        except Exception as e:
            await send_telegram_log(f"❌ Cancel failed: {order_id} - {e}", tag="error")
            return {"error": str(e)}

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker information."""
        if not self.exchange or not self.enable_live_trading:
            # Mock implementation with realistic crypto prices
            mock_prices = {
                "BTCUSDT": "43250.5",
                "ETHUSDT": "2580.25", 
                "XRPUSDT": "0.6245",
                "SOLUSDT": "98.75"
            }
            base_price = float(mock_prices.get(symbol, "50000.0"))
            return {
                "symbol": symbol,
                "last": base_price,
                "bid": base_price * 0.9999,
                "ask": base_price * 1.0001,
                "timestamp": int(time.time() * 1000)
            }
        
        try:
            ticker = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.fetch_ticker, symbol
            )
            return ticker
        except Exception as e:
            await send_telegram_log(f"❌ Error fetching ticker {symbol}: {e}", tag="error")
            return {"error": str(e)}

    async def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        ticker = await self.get_ticker(symbol)
        if "error" in ticker:
            return 0.0
        return float(ticker.get("last", 0.0))

    def is_live_trading_enabled(self) -> bool:
        """Check if live trading is enabled."""
        return self.enable_live_trading and self.exchange is not None

# Create a global client instance for imports
client = BitgetClient()
print("📡 Mock Bitget client initialized")
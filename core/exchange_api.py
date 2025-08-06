# Enhanced Exchange API Integration for Bybit and Bitget
"""
Comprehensive trading API integration supporting both Bybit and Bitget exchanges.
Features: Real-time pricing, balance management, dual LIMIT orders, error handling with retries.
"""

import asyncio
import time
import os
import ccxt
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from utils.telegram_logger import send_telegram_log
from config.settings import ExchangeConfig

@dataclass
class OrderResult:
    """Standardized order result structure."""
    order_id: str
    status: str
    symbol: str
    side: str
    amount: float
    price: float = None
    filled: float = 0.0
    remaining: float = 0.0
    cost: float = 0.0
    timestamp: datetime = None
    raw_response: dict = None

@dataclass
class PositionInfo:
    """Position information structure."""
    symbol: str
    side: str
    size: float
    entry_price: float
    unrealized_pnl: float
    percentage: float
    leverage: float
    margin: float

class RateLimiter:
    """Advanced rate limiting system."""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.locked_until = None
    
    async def acquire(self):
        """Acquire rate limit permission."""
        now = time.time()
        
        # Check if we're in a locked state
        if self.locked_until and now < self.locked_until:
            wait_time = self.locked_until - now
            print(f"⏳ Rate limit active, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            return
        
        # Clean old requests
        self.requests = [req for req in self.requests if now - req < self.time_window]
        
        # Check if we can make a request
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0])
            print(f"⏳ Rate limit reached, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        self.requests.append(now)
    
    def set_penalty(self, duration: int = 60):
        """Set a penalty period for rate limit violations."""
        self.locked_until = time.time() + duration

class ExchangeAPI:
    """Unified exchange API supporting both Bybit and Bitget."""
    
    def __init__(self, exchange_name: str = "bitget", testnet: bool = True):
        self.exchange_name = exchange_name.lower()
        self.testnet = testnet
        self.exchange = None
        self.rate_limiter = RateLimiter(max_requests=10, time_window=60)
        
        # API credentials from environment
        self.api_key = os.getenv(f'{exchange_name.upper()}_API_KEY', '')
        self.api_secret = os.getenv(f'{exchange_name.upper()}_API_SECRET', '')
        self.api_passphrase = os.getenv(f'{exchange_name.upper()}_API_PASSPHRASE', '')
        
        # Determine mock mode based on credentials
        self.mock_mode = not all([self.api_key, self.api_secret])
        
        # Initialize exchange
        self._initialize_exchange()
        
        if self.mock_mode:
            print(f"⚠️ {exchange_name.upper()} API running in MOCK MODE (add credentials for live trading)")
        else:
            print(f"✅ {exchange_name.upper()} API initialized {'(TESTNET)' if testnet else '(LIVE)'}")
    
    def _initialize_exchange(self):
        """Initialize the exchange client."""
        try:
            if self.exchange_name == "bitget":
                self.exchange = ccxt.bitget({
                    'apiKey': self.api_key,
                    'secret': self.api_secret,
                    'password': self.api_passphrase,
                    'sandbox': self.testnet,
                    'enableRateLimit': True,
                    'rateLimit': 100,  # 100ms between requests
                })
            elif self.exchange_name == "bybit":
                self.exchange = ccxt.bybit({
                    'apiKey': self.api_key,
                    'secret': self.api_secret,
                    'sandbox': self.testnet,
                    'enableRateLimit': True,
                    'rateLimit': 100,
                })
            else:
                raise ValueError(f"Unsupported exchange: {self.exchange_name}")
                
            # Test connection if credentials are provided
            if not self.mock_mode:
                self.exchange.load_markets()
                
        except Exception as e:
            print(f"❌ Failed to initialize {self.exchange_name}: {e}")
            self.mock_mode = True
    
    async def _execute_with_retry(self, func, *args, max_retries: int = 3, **kwargs) -> Any:
        """Execute API call with retry logic and rate limiting."""
        await self.rate_limiter.acquire()
        
        for attempt in range(max_retries):
            try:
                if self.mock_mode:
                    return await self._mock_response(func.__name__, *args, **kwargs)
                
                result = func(*args, **kwargs)
                return result
                
            except ccxt.RateLimitExceeded as e:
                wait_time = min(60 * (2 ** attempt), 300)  # Exponential backoff, max 5 minutes
                print(f"⚠️ Rate limit exceeded, waiting {wait_time}s (attempt {attempt + 1})")
                self.rate_limiter.set_penalty(wait_time)
                await asyncio.sleep(wait_time)
                
            except ccxt.NetworkError as e:
                wait_time = min(10 * (2 ** attempt), 60)  # Network backoff, max 1 minute
                print(f"⚠️ Network error, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
                
            except ccxt.ExchangeError as e:
                print(f"❌ Exchange error: {e}")
                if "insufficient" in str(e).lower():
                    raise ValueError("Insufficient balance for trade")
                elif "invalid" in str(e).lower():
                    raise ValueError(f"Invalid order parameters: {e}")
                else:
                    raise e
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"❌ API call failed after {max_retries} attempts: {e}")
                    raise e
                await asyncio.sleep(2 ** attempt)
        
        raise Exception(f"Failed to execute {func.__name__} after {max_retries} attempts")
    
    async def _mock_response(self, method_name: str, *args, **kwargs) -> Any:
        """Generate mock responses for testing."""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        if method_name == "fetch_ticker":
            symbol = args[0] if args else "BTCUSDT"
            base_price = {"BTCUSDT": 67000, "ETHUSDT": 3800, "SOLUSDT": 180}.get(symbol, 50000)
            return {
                'symbol': symbol,
                'last': base_price + (time.time() % 100 - 50),  # Simulate price movement
                'bid': base_price - 1,
                'ask': base_price + 1,
                'high': base_price + 500,
                'low': base_price - 500,
                'volume': 1000000,
                'timestamp': int(time.time() * 1000)
            }
        
        elif method_name == "fetch_balance":
            return {
                'USDT': {'free': 10000.0, 'used': 0.0, 'total': 10000.0},
                'BTC': {'free': 0.5, 'used': 0.0, 'total': 0.5},
                'ETH': {'free': 2.0, 'used': 0.0, 'total': 2.0}
            }
        
        elif method_name == "create_order":
            return {
                'id': f'mock_{int(time.time())}_{hash(str(args))%10000}',
                'timestamp': int(time.time() * 1000),
                'status': 'open',
                'symbol': kwargs.get('symbol', args[0] if args else 'BTCUSDT'),
                'side': kwargs.get('side', args[1] if len(args) > 1 else 'buy'),
                'amount': kwargs.get('amount', args[2] if len(args) > 2 else 0.01),
                'price': kwargs.get('price', args[3] if len(args) > 3 else 67000),
                'filled': 0.0,
                'remaining': kwargs.get('amount', args[2] if len(args) > 2 else 0.01),
                'cost': 0.0,
                'info': {'orderId': f'mock_{int(time.time())}'}
            }
        
        elif method_name == "fetch_positions":
            return [{
                'symbol': kwargs.get('symbol', 'BTCUSDT'),
                'side': 'long',
                'size': 0.0,
                'contracts': 0.0,
                'unrealizedPnl': 0.0,
                'percentage': 0.0,
                'entryPrice': 0.0,
                'markPrice': 67000.0,
                'leverage': 10
            }]
        
        return {'status': 'mock', 'method': method_name, 'args': args, 'kwargs': kwargs}
    
    async def get_current_price(self, symbol: str) -> float:
        """Fetch current price for a symbol."""
        try:
            ticker = await self._execute_with_retry(self.exchange.fetch_ticker, symbol)
            price = ticker['last']
            print(f"💰 {symbol}: ${price:,.2f}")
            return price
        except Exception as e:
            print(f"❌ Failed to get price for {symbol}: {e}")
            await send_telegram_log(f"⚠️ Price fetch failed for {symbol}: {e}")
            return None
    
    async def get_balance(self, currency: str = None) -> Dict[str, Dict[str, float]]:
        """Fetch account balance."""
        try:
            balance = await self._execute_with_retry(self.exchange.fetch_balance)
            
            if currency:
                return balance.get(currency, {'free': 0.0, 'used': 0.0, 'total': 0.0})
            
            # Filter out zero balances
            filtered_balance = {
                curr: info for curr, info in balance.items()
                if isinstance(info, dict) and info.get('total', 0) > 0
            }
            
            print(f"💼 Account Balance: {len(filtered_balance)} currencies with balance")
            for curr, info in list(filtered_balance.items())[:5]:  # Show top 5
                print(f"   {curr}: {info['total']:.6f} (Free: {info['free']:.6f})")
            
            return filtered_balance
            
        except Exception as e:
            print(f"❌ Failed to get balance: {e}")
            await send_telegram_log(f"⚠️ Balance fetch failed: {e}")
            return {}
    
    async def place_limit_order(self, symbol: str, side: str, amount: float, 
                               price: float, reduce_only: bool = False) -> OrderResult:
        """Place a limit order."""
        try:
            params = {}
            if reduce_only:
                params['reduceOnly'] = True
            
            order = await self._execute_with_retry(
                self.exchange.create_order,
                symbol=symbol,
                type='limit',
                side=side,
                amount=amount,
                price=price,
                params=params
            )
            
            result = OrderResult(
                order_id=order['id'],
                status=order['status'],
                symbol=order['symbol'],
                side=order['side'],
                amount=order['amount'],
                price=order['price'],
                filled=order['filled'],
                remaining=order['remaining'],
                cost=order['cost'],
                timestamp=datetime.fromtimestamp(order['timestamp'] / 1000),
                raw_response=order
            )
            
            print(f"📤 LIMIT ORDER: {side.upper()} {amount} {symbol} @ ${price:,.2f}")
            print(f"   Order ID: {result.order_id}")
            print(f"   Status: {result.status}")
            
            await send_telegram_log(
                f"📤 Order placed: {side.upper()} {amount} {symbol} @ ${price:,.2f}\nID: {result.order_id}"
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to place limit order: {e}")
            await send_telegram_log(f"❌ Order failed: {side.upper()} {amount} {symbol} @ ${price:,.2f}\nError: {e}")
            raise e
    
    async def place_dual_limit_orders(self, symbol: str, side: str, total_amount: float,
                                     entry_price1: float, entry_price2: float,
                                     step1_ratio: float = 0.6) -> Tuple[OrderResult, OrderResult]:
        """
        Place dual LIMIT orders for entry (Step 1 and Step 2).
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'buy' or 'sell'
            total_amount: Total position size
            entry_price1: Price for first order (Step 1)
            entry_price2: Price for second order (Step 2)
            step1_ratio: Ratio of total amount for step 1 (default 60%)
        """
        try:
            # Calculate amounts for each step
            step1_amount = round(total_amount * step1_ratio, 6)
            step2_amount = round(total_amount * (1 - step1_ratio), 6)
            
            print(f"🎯 DUAL ENTRY STRATEGY for {symbol}")
            print(f"   Total Amount: {total_amount}")
            print(f"   Step 1: {step1_amount} @ ${entry_price1:,.2f} ({step1_ratio*100:.0f}%)")
            print(f"   Step 2: {step2_amount} @ ${entry_price2:,.2f} ({(1-step1_ratio)*100:.0f}%)")
            
            # Place both orders concurrently
            order1_task = self.place_limit_order(symbol, side, step1_amount, entry_price1)
            order2_task = self.place_limit_order(symbol, side, step2_amount, entry_price2)
            
            order1, order2 = await asyncio.gather(order1_task, order2_task)
            
            print("✅ DUAL ORDERS PLACED SUCCESSFULLY")
            await send_telegram_log(
                f"✅ Dual Entry Orders Placed for {symbol}\n"
                f"Step 1: {step1_amount} @ ${entry_price1:,.2f} (ID: {order1.order_id})\n"
                f"Step 2: {step2_amount} @ ${entry_price2:,.2f} (ID: {order2.order_id})"
            )
            
            return order1, order2
            
        except Exception as e:
            print(f"❌ Failed to place dual orders: {e}")
            await send_telegram_log(f"❌ Dual order placement failed for {symbol}: {e}")
            raise e
    
    async def get_positions(self, symbol: str = None) -> List[PositionInfo]:
        """Fetch current positions."""
        try:
            positions = await self._execute_with_retry(self.exchange.fetch_positions, symbol)
            
            active_positions = []
            for pos in positions:
                if pos['contracts'] != 0:  # Only active positions
                    position_info = PositionInfo(
                        symbol=pos['symbol'],
                        side=pos['side'],
                        size=pos['contracts'],
                        entry_price=pos['entryPrice'] or 0,
                        unrealized_pnl=pos['unrealizedPnl'] or 0,
                        percentage=pos['percentage'] or 0,
                        leverage=pos['leverage'] or 1,
                        margin=pos.get('initialMargin', 0)
                    )
                    active_positions.append(position_info)
            
            if active_positions:
                print(f"📊 Active Positions: {len(active_positions)}")
                for pos in active_positions:
                    pnl_emoji = "🟢" if pos.unrealized_pnl >= 0 else "🔴"
                    print(f"   {pos.symbol} {pos.side.upper()}: {pos.size:.6f} @ ${pos.entry_price:,.2f}")
                    print(f"   {pnl_emoji} PnL: ${pos.unrealized_pnl:,.2f} ({pos.percentage:+.2f}%)")
            else:
                print("📊 No active positions")
            
            return active_positions
            
        except Exception as e:
            print(f"❌ Failed to get positions: {e}")
            await send_telegram_log(f"⚠️ Position fetch failed: {e}")
            return []
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order."""
        try:
            result = await self._execute_with_retry(self.exchange.cancel_order, order_id, symbol)
            print(f"🗑️ Order cancelled: {order_id}")
            await send_telegram_log(f"🗑️ Order cancelled: {order_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to cancel order {order_id}: {e}")
            await send_telegram_log(f"❌ Cancel failed for order {order_id}: {e}")
            return False
    
    async def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """Get order status."""
        try:
            order = await self._execute_with_retry(self.exchange.fetch_order, order_id, symbol)
            print(f"📋 Order {order_id}: {order['status']} - {order['filled']}/{order['amount']} filled")
            return order
        except Exception as e:
            print(f"❌ Failed to get order status {order_id}: {e}")
            return None
    
    def is_live_trading_enabled(self) -> bool:
        """Check if live trading is enabled."""
        return not self.mock_mode and not self.testnet

# Global exchange instances
bitget_api = ExchangeAPI("bitget", testnet=False)
bybit_api = ExchangeAPI("bybit", testnet=False)

# Convenience functions for backward compatibility
async def get_current_price(symbol: str) -> float:
    """Get current price using the default exchange."""
    return await bitget_api.get_current_price(symbol)

async def place_dual_entry_orders(symbol: str, side: str, total_amount: float,
                                 entry_price1: float, entry_price2: float) -> Tuple[OrderResult, OrderResult]:
    """Place dual entry orders using the default exchange."""
    return await bitget_api.place_dual_limit_orders(symbol, side, total_amount, entry_price1, entry_price2)

if __name__ == "__main__":
    # Example usage and testing
    async def test_api():
        print("🧪 Testing Exchange API Integration...")
        
        # Test price fetching
        btc_price = await bitget_api.get_current_price("BTCUSDT")
        eth_price = await bitget_api.get_current_price("ETHUSDT")
        
        # Test balance
        balance = await bitget_api.get_balance()
        
        # Test positions
        positions = await bitget_api.get_positions()
        
        # Test dual orders (mock)
        try:
            order1, order2 = await bitget_api.place_dual_limit_orders(
                "BTCUSDT", "buy", 0.01, 66000, 65500
            )
            print(f"Dual orders: {order1.order_id}, {order2.order_id}")
        except Exception as e:
            print(f"Dual order test failed: {e}")
    
    import asyncio
    asyncio.run(test_api())
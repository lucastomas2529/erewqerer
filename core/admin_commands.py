#!/usr/bin/env python3
"""
Admin command system for manual trading control via Telegram.
Provides commands for buy, sell, close, modify, and system overrides.
"""

import asyncio
import re
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from core.api import (
    place_market_order, place_limit_order, cancel_order, 
    get_current_price_async, get_account_balance
)
from core.entry_manager import execute_entry_strategy
from core.breakeven_manager import breakeven_manager
from core.trailing_manager import trailing_manager
from core.timeout_manager import timeout_manager
from core.reporting_system import reporting_system
from config.settings import TradingConfig, OverrideConfig
from utils.telegram_logger import send_telegram_log
from utils.logger import log_event

class AdminCommandHandler:
    """Handles admin commands for manual trading control."""
    
    def __init__(self):
        self.authorized_users = [7617377640]  # Admin user IDs
        self.command_history = []
        self.active_commands = {}
        
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use admin commands."""
        return user_id in self.authorized_users
    
    async def handle_command(self, user_id: int, command: str, args: List[str]) -> str:
        """Handle admin commands and return response."""
        if not self.is_authorized(user_id):
            return "❌ Unauthorized access. Admin commands only."
        
        try:
            # Parse command
            cmd = command.lower().strip('/')
            
            if cmd == "buy":
                return await self.handle_buy_command(args)
            elif cmd == "sell":
                return await self.handle_sell_command(args)
            elif cmd == "close":
                return await self.handle_close_command(args)
            elif cmd == "modify":
                return await self.handle_modify_command(args)
            elif cmd == "status":
                return await self.handle_status_command(args)
            elif cmd == "override":
                return await self.handle_override_command(args)
            elif cmd == "help":
                return self.get_help_message()
            else:
                return f"❌ Unknown command: {command}\nUse /help for available commands."
                
        except Exception as e:
            log_event(f"❌ Admin command error: {e}", "ERROR")
            return f"❌ Command failed: {str(e)}"
    
    async def handle_buy_command(self, args: List[str]) -> str:
        """Handle /buy command for manual buy orders."""
        if len(args) < 2:
            return "❌ Usage: /buy <symbol> <quantity> [price] [sl] [tp]"
        
        try:
            symbol = args[0].upper()
            quantity = float(args[1])
            price = float(args[2]) if len(args) > 2 else None
            sl_price = float(args[3]) if len(args) > 3 else None
            tp_price = float(args[4]) if len(args) > 4 else None
            
            # Get current price if not specified
            if not price:
                current_price = await get_current_price_async(symbol)
                price = current_price
            
            # Place order
            if price:
                # Place limit order
                order = await place_limit_order(symbol, "buy", quantity, price)
                order_type = "LIMIT"
            else:
                # Place market order
                order = place_market_order(symbol, quantity, "buy")
                order_type = "MARKET"
            
            if order and order.get("order_id"):
                # Register for monitoring
                await self.register_trade_for_monitoring(
                    symbol, "buy", price or order.get("price"), 
                    sl_price, [tp_price] if tp_price else [], 
                    [order["order_id"]], quantity
                )
                
                # Log trade with reporting system
                await reporting_system.log_trade({
                    'symbol': symbol,
                    'side': 'buy',
                    'quantity': quantity,
                    'entry_price': price or order.get("price"),
                    'sl_price': sl_price,
                    'tp_prices': [tp_price] if tp_price else [],
                    'order_ids': [order["order_id"]],
                    'group_name': 'Admin Command',
                    'signal_source': 'admin_command',
                    'processing_time': 0.0,
                    'admin_command': True
                })
                
                response = f"✅ BUY {order_type} ORDER PLACED\n"
                response += f"Symbol: {symbol}\n"
                response += f"Quantity: {quantity}\n"
                response += f"Price: ${price or order.get('price'):,.2f}\n"
                response += f"Order ID: {order['order_id']}\n"
                
                if sl_price:
                    response += f"SL: ${sl_price:,.2f}\n"
                if tp_price:
                    response += f"TP: ${tp_price:,.2f}\n"
                
                log_event(f"Admin BUY order: {symbol} {quantity} @ ${price}", "INFO")
                return response
            else:
                return "❌ Failed to place buy order"
                
        except ValueError as e:
            return f"❌ Invalid parameters: {str(e)}"
        except Exception as e:
            return f"❌ Buy order failed: {str(e)}"
    
    async def handle_sell_command(self, args: List[str]) -> str:
        """Handle /sell command for manual sell orders."""
        if len(args) < 2:
            return "❌ Usage: /sell <symbol> <quantity> [price] [sl] [tp]"
        
        try:
            symbol = args[0].upper()
            quantity = float(args[1])
            price = float(args[2]) if len(args) > 2 else None
            sl_price = float(args[3]) if len(args) > 3 else None
            tp_price = float(args[4]) if len(args) > 4 else None
            
            # Get current price if not specified
            if not price:
                current_price = await get_current_price_async(symbol)
                price = current_price
            
            # Place order
            if price:
                # Place limit order
                order = await place_limit_order(symbol, "sell", quantity, price)
                order_type = "LIMIT"
            else:
                # Place market order
                order = place_market_order(symbol, quantity, "sell")
                order_type = "MARKET"
            
            if order and order.get("order_id"):
                # Register for monitoring
                await self.register_trade_for_monitoring(
                    symbol, "sell", price or order.get("price"), 
                    sl_price, [tp_price] if tp_price else [], 
                    [order["order_id"]], quantity
                )
                
                # Log trade with reporting system
                await reporting_system.log_trade({
                    'symbol': symbol,
                    'side': 'sell',
                    'quantity': quantity,
                    'entry_price': price or order.get("price"),
                    'sl_price': sl_price,
                    'tp_prices': [tp_price] if tp_price else [],
                    'order_ids': [order["order_id"]],
                    'group_name': 'Admin Command',
                    'signal_source': 'admin_command',
                    'processing_time': 0.0,
                    'admin_command': True
                })
                
                response = f"✅ SELL {order_type} ORDER PLACED\n"
                response += f"Symbol: {symbol}\n"
                response += f"Quantity: {quantity}\n"
                response += f"Price: ${price or order.get('price'):,.2f}\n"
                response += f"Order ID: {order['order_id']}\n"
                
                if sl_price:
                    response += f"SL: ${sl_price:,.2f}\n"
                if tp_price:
                    response += f"TP: ${tp_price:,.2f}\n"
                
                log_event(f"Admin SELL order: {symbol} {quantity} @ ${price}", "INFO")
                return response
            else:
                return "❌ Failed to place sell order"
                
        except ValueError as e:
            return f"❌ Invalid parameters: {str(e)}"
        except Exception as e:
            return f"❌ Sell order failed: {str(e)}"
    
    async def handle_close_command(self, args: List[str]) -> str:
        """Handle /close command to close positions."""
        if len(args) < 1:
            return "❌ Usage: /close <symbol> [quantity]"
        
        try:
            symbol = args[0].upper()
            quantity = float(args[1]) if len(args) > 1 else None
            
            # Get current price
            current_price = await get_current_price_async(symbol)
            
            # Determine side based on active trades
            side = "sell"  # Default to sell (close long position)
            
            # Check if we have active trades for this symbol
            if symbol in breakeven_manager.active_trades:
                trade = breakeven_manager.active_trades[symbol]
                side = "sell" if trade["side"] == "buy" else "buy"
                if not quantity:
                    quantity = trade.get("quantity", 0.001)
            
            if not quantity:
                quantity = 0.001  # Default quantity
            
            # Place market order to close
            order = place_market_order(symbol, quantity, side)
            
            if order and order.get("order_id"):
                # Close monitoring for this symbol
                await self.close_trade_monitoring(symbol)
                
                response = f"✅ POSITION CLOSED\n"
                response += f"Symbol: {symbol}\n"
                response += f"Side: {side.upper()}\n"
                response += f"Quantity: {quantity}\n"
                response += f"Price: ${current_price:,.2f}\n"
                response += f"Order ID: {order['order_id']}\n"
                
                log_event(f"Admin CLOSE order: {symbol} {quantity} @ ${current_price}", "INFO")
                return response
            else:
                return "❌ Failed to close position"
                
        except Exception as e:
            return f"❌ Close order failed: {str(e)}"
    
    async def handle_modify_command(self, args: List[str]) -> str:
        """Handle /modify command to modify trade parameters."""
        if len(args) < 3:
            return "❌ Usage: /modify <symbol> <parameter> <value>"
        
        try:
            symbol = args[0].upper()
            parameter = args[1].lower()
            value = args[2]
            
            if parameter == "sl":
                new_sl = float(value)
                success = await self.modify_sl(symbol, new_sl)
                if success:
                    return f"✅ SL modified for {symbol}: ${new_sl:,.2f}"
                else:
                    return f"❌ Failed to modify SL for {symbol}"
                    
            elif parameter == "tp":
                new_tp = float(value)
                success = await self.modify_tp(symbol, new_tp)
                if success:
                    return f"✅ TP modified for {symbol}: ${new_tp:,.2f}"
                else:
                    return f"❌ Failed to modify TP for {symbol}"
                    
            elif parameter == "quantity":
                new_qty = float(value)
                success = await self.modify_quantity(symbol, new_qty)
                if success:
                    return f"✅ Quantity modified for {symbol}: {new_qty}"
                else:
                    return f"❌ Failed to modify quantity for {symbol}"
                    
            else:
                return f"❌ Unknown parameter: {parameter}\nSupported: sl, tp, quantity"
                
        except ValueError as e:
            return f"❌ Invalid value: {str(e)}"
        except Exception as e:
            return f"❌ Modify failed: {str(e)}"
    
    async def handle_status_command(self, args: List[str]) -> str:
        """Handle /status command to show system status."""
        try:
            response = "📊 SYSTEM STATUS\n"
            response += "=" * 30 + "\n"
            
            # Active trades
            breakeven_trades = len(breakeven_manager.active_trades)
            trailing_trades = len(trailing_manager.active_trades)
            timeout_trades = len(timeout_manager.active_trades)
            
            response += f"Active Trades:\n"
            response += f"  Break-even: {breakeven_trades}\n"
            response += f"  Trailing: {trailing_trades}\n"
            response += f"  Timeout: {timeout_trades}\n\n"
            
            # System overrides
            response += f"System Overrides:\n"
            response += f"  Pyramiding: {'✅' if OverrideConfig.ENABLE_PYRAMIDING else '❌'}\n"
            response += f"  Re-entry: {'✅' if OverrideConfig.ENABLE_REENTRY else '❌'}\n"
            response += f"  Hedging: {'✅' if OverrideConfig.ENABLE_HEDGING else '❌'}\n"
            response += f"  Trailing: {'✅' if TradingConfig.USE_TRAILING_SL else '❌'}\n"
            response += f"  Debug Mode: {'✅' if OverrideConfig.DEBUG_MODE else '❌'}\n\n"
            
            # Account balance
            try:
                balance = await get_account_balance("USDT")
                response += f"Account Balance: ${balance:,.2f} USDT\n"
            except:
                response += f"Account Balance: Unable to fetch\n"
            
            return response
            
        except Exception as e:
            return f"❌ Status check failed: {str(e)}"
    
    async def handle_override_command(self, args: List[str]) -> str:
        """Handle /override command to toggle system features."""
        if len(args) < 2:
            return "❌ Usage: /override <feature> <on/off>"
        
        try:
            feature = args[0].lower()
            state = args[1].lower()
            
            if state not in ["on", "off"]:
                return "❌ State must be 'on' or 'off'"
            
            enabled = state == "on"
            
            if feature == "pyramiding":
                OverrideConfig.ENABLE_PYRAMIDING = enabled
                response = f"Pyramiding: {'✅ ON' if enabled else '❌ OFF'}"
            elif feature == "reentry":
                OverrideConfig.ENABLE_REENTRY = enabled
                response = f"Re-entry: {'✅ ON' if enabled else '❌ OFF'}"
            elif feature == "hedging":
                OverrideConfig.ENABLE_HEDGING = enabled
                response = f"Hedging: {'✅ ON' if enabled else '❌ OFF'}"
            elif feature == "trailing":
                TradingConfig.USE_TRAILING_SL = enabled
                response = f"Trailing: {'✅ ON' if enabled else '❌ OFF'}"
            elif feature == "debug":
                OverrideConfig.DEBUG_MODE = enabled
                response = f"Debug Mode: {'✅ ON' if enabled else '❌ OFF'}"
            else:
                return f"❌ Unknown feature: {feature}\nSupported: pyramiding, reentry, hedging, trailing, debug"
            
            log_event(f"Admin override: {feature} -> {state}", "INFO")
            return f"✅ {response}"
            
        except Exception as e:
            return f"❌ Override failed: {str(e)}"
    
    async def register_trade_for_monitoring(self, symbol: str, side: str, entry_price: float,
                                          sl_price: float, tp_prices: List[float], 
                                          order_ids: List[str], quantity: float):
        """Register trade with all monitoring systems."""
        try:
            # Register with break-even manager
            await breakeven_manager.register_trade(
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                sl_price=sl_price,
                tp_prices=tp_prices,
                order_ids=order_ids
            )
            
            # Register with trailing manager
            await trailing_manager.register_trade(
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                sl_price=sl_price,
                tp_prices=tp_prices,
                order_ids=order_ids
            )
            
            # Register with timeout manager
            await timeout_manager.register_trade(
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                sl_price=sl_price,
                tp_prices=tp_prices,
                order_ids=order_ids,
                quantity=quantity
            )
            
        except Exception as e:
            log_event(f"❌ Failed to register trade for monitoring: {e}", "ERROR")
    
    async def close_trade_monitoring(self, symbol: str):
        """Close monitoring for a specific symbol."""
        try:
            # Close in all managers
            breakeven_manager.close_trade(symbol)
            trailing_manager.close_trade(symbol)
            timeout_manager.close_trade(symbol)
            
        except Exception as e:
            log_event(f"❌ Failed to close trade monitoring: {e}", "ERROR")
    
    async def modify_sl(self, symbol: str, new_sl: float) -> bool:
        """Modify stop-loss for a symbol."""
        try:
            # Update in break-even manager
            if symbol in breakeven_manager.active_trades:
                breakeven_manager.active_trades[symbol]["sl_price"] = new_sl
            
            # Update in trailing manager
            if symbol in trailing_manager.active_trades:
                trailing_manager.active_trades[symbol]["sl_price"] = new_sl
            
            # Update in timeout manager
            if symbol in timeout_manager.active_trades:
                timeout_manager.active_trades[symbol]["sl_price"] = new_sl
            
            log_event(f"SL modified for {symbol}: ${new_sl:,.2f}", "INFO")
            return True
            
        except Exception as e:
            log_event(f"❌ Failed to modify SL: {e}", "ERROR")
            return False
    
    async def modify_tp(self, symbol: str, new_tp: float) -> bool:
        """Modify take-profit for a symbol."""
        try:
            # Update in break-even manager
            if symbol in breakeven_manager.active_trades:
                breakeven_manager.active_trades[symbol]["tp_prices"] = [new_tp]
            
            # Update in trailing manager
            if symbol in trailing_manager.active_trades:
                trailing_manager.active_trades[symbol]["tp_prices"] = [new_tp]
            
            # Update in timeout manager
            if symbol in timeout_manager.active_trades:
                timeout_manager.active_trades[symbol]["tp_prices"] = [new_tp]
            
            log_event(f"TP modified for {symbol}: ${new_tp:,.2f}", "INFO")
            return True
            
        except Exception as e:
            log_event(f"❌ Failed to modify TP: {e}", "ERROR")
            return False
    
    async def modify_quantity(self, symbol: str, new_qty: float) -> bool:
        """Modify quantity for a symbol."""
        try:
            # Update in timeout manager
            if symbol in timeout_manager.active_trades:
                timeout_manager.active_trades[symbol]["quantity"] = new_qty
            
            log_event(f"Quantity modified for {symbol}: {new_qty}", "INFO")
            return True
            
        except Exception as e:
            log_event(f"❌ Failed to modify quantity: {e}", "ERROR")
            return False
    
    def get_help_message(self) -> str:
        """Get help message with all available commands."""
        help_msg = """
🤖 ADMIN COMMANDS HELP
======================

📈 TRADING COMMANDS:
/buy <symbol> <quantity> [price] [sl] [tp]
   Place a buy order
   Example: /buy BTCUSDT 0.001 67000 65000 70000

/sell <symbol> <quantity> [price] [sl] [tp]
   Place a sell order
   Example: /sell ETHUSDT 0.1 3750 3650 3900

/close <symbol> [quantity]
   Close a position
   Example: /close BTCUSDT 0.001

/modify <symbol> <parameter> <value>
   Modify trade parameters
   Parameters: sl, tp, quantity
   Example: /modify BTCUSDT sl 65000

📊 SYSTEM COMMANDS:
/status
   Show system status and active trades

/override <feature> <on/off>
   Toggle system features
   Features: pyramiding, reentry, hedging, trailing, debug
   Example: /override pyramiding off

/help
   Show this help message

⚠️ NOTES:
- All prices should be in USD
- Quantities should be in base currency
- Only authorized users can use admin commands
- Use with caution in live trading
        """
        return help_msg.strip()

# Global instance
admin_handler = AdminCommandHandler()

# Test function
async def test_admin_commands():
    """Test the admin command system."""
    print("🧪 TESTING ADMIN COMMANDS")
    print("=" * 40)
    
    # Test help command
    help_msg = admin_handler.get_help_message()
    print("✅ Help message generated")
    
    # Test authorization
    authorized = admin_handler.is_authorized(7617377640)
    print(f"✅ Authorization test: {authorized}")
    
    # Test status command
    status = await admin_handler.handle_status_command([])
    print("✅ Status command working")
    
    print("✅ Admin command system test completed!")

if __name__ == "__main__":
    asyncio.run(test_admin_commands()) 
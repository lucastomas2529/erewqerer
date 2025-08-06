# reentry_watcher.py – Automatic re-entry functionality

import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime
from config.settings import TradingConfig
from utils.telegram_logger import send_telegram_log
from core.api import get_position, place_market_order
from core.symbol_data import get_symbol_precision
from utils.quantity import calculate_quantity
from logic.entry import handle_entry_signal

logger = logging.getLogger(__name__)

class ReentryWatcher:
    """
    Monitors closed trades and attempts automatic re-entry after configurable delays.
    Implements re-entry logic with risk management and validation checks.
    """
    
    def __init__(self):
        self.reentry_tasks: Dict[str, asyncio.Task] = {}
        self.reentry_active: Dict[str, bool] = {}
        self.reentry_attempts: Dict[str, int] = {}  # symbol -> number of attempts
        self.original_signals: Dict[str, dict] = {}  # symbol -> original signal data
        self.entry_prices: Dict[str, float] = {}
        self.reentry_enabled = TradingConfig.REENTRY_ENABLED
        self.max_attempts = TradingConfig.REENTRY_MAX_ATTEMPTS
        self.reentry_delay = TradingConfig.REENTRY_DELAY
        self.price_deviation = TradingConfig.REENTRY_PRICE_DEVIATION
        logger.info(f"🔄 ReentryWatcher initialized with {self.max_attempts} max attempts, {self.reentry_delay}s delay")
    
    async def start_reentry_watcher(self, symbol: str, original_signal: dict, 
                                  entry_price: float, exit_reason: str, group_name: str = None):
        """
        Start re-entry watcher for a closed trade.
        
        Args:
            symbol: Trading symbol
            original_signal: Original signal data for re-entry validation
            entry_price: Original entry price
            exit_reason: Reason for exit ('SL', 'TP', 'manual', etc.)
            group_name: Optional group name for logging
        """
        try:
            # Check if re-entry is enabled
            if not self.reentry_enabled:
                logger.info(f"[Re-entry] Re-entry disabled for {symbol}")
                return
            
            # Cancel existing re-entry task if any
            await self.cancel_reentry_watcher(symbol)
            
            # Initialize re-entry state
            self.reentry_active[symbol] = True
            self.reentry_attempts[symbol] = 0
            self.original_signals[symbol] = original_signal
            self.entry_prices[symbol] = entry_price
            
            # Create re-entry task
            reentry_task = asyncio.create_task(
                self._reentry_handler(symbol, original_signal, entry_price, exit_reason, group_name),
                name=f"reentry_{symbol}"
            )
            
            self.reentry_tasks[symbol] = reentry_task
            
            log_message = f"🔄 Re-entry watcher started for {symbol} after {exit_reason} (delay: {self.reentry_delay}s, max attempts: {self.max_attempts})"
            
            if group_name:
                await send_telegram_log(log_message, group_name=group_name, tag="reentry")
            else:
                await send_telegram_log(log_message, tag="reentry")
            
            logger.info(f"[Re-entry] Watcher started for {symbol} after {exit_reason} (delay: {self.reentry_delay}s)")
            
        except Exception as e:
            logger.error(f"❌ Failed to start re-entry watcher for {symbol}: {e}")
    
    async def _reentry_handler(self, symbol: str, original_signal: dict, 
                             entry_price: float, exit_reason: str, group_name: str = None):
        """
        Handle re-entry monitoring for a specific symbol.
        """
        try:
            # Wait for the configured delay
            logger.info(f"[Re-entry] Waiting {self.reentry_delay}s before attempting re-entry for {symbol}")
            await asyncio.sleep(self.reentry_delay)
            
            # Check if re-entry is still active after delay
            if not self.reentry_active.get(symbol, False):
                logger.info(f"[Re-entry] Re-entry cancelled for {symbol} during delay")
                return
            
            # Attempt re-entry
            await self._attempt_reentry(symbol, original_signal, entry_price, exit_reason, group_name)
            
        except asyncio.CancelledError:
            logger.info(f"[Re-entry] Watcher cancelled for {symbol} (re-entry disabled)")
        except Exception as e:
            logger.error(f"❌ Error in re-entry handler for {symbol}: {e}")
    
    async def _attempt_reentry(self, symbol: str, original_signal: dict, 
                             entry_price: float, exit_reason: str, group_name: str = None):
        """
        Attempt re-entry for a symbol.
        """
        try:
            # Check if max attempts reached
            current_attempts = self.reentry_attempts.get(symbol, 0)
            if current_attempts >= self.max_attempts:
                log_message = f"🔄 [Re-entry] Max attempts ({self.max_attempts}) reached for {symbol} - stopping re-entry"
                if group_name:
                    await send_telegram_log(log_message, group_name=group_name, tag="reentry")
                else:
                    await send_telegram_log(log_message, tag="reentry")
                logger.info(f"[Re-entry] Max attempts reached for {symbol}")
                await self.cancel_reentry_watcher(symbol)
                return
            
            # Check if symbol is blacklisted
            if await self._is_symbol_blacklisted(symbol):
                log_message = f"🔄 [Re-entry] {symbol} is blacklisted - skipping re-entry"
                if group_name:
                    await send_telegram_log(log_message, group_name=group_name, tag="reentry")
                else:
                    await send_telegram_log(log_message, tag="reentry")
                logger.info(f"[Re-entry] {symbol} is blacklisted")
                await self.cancel_reentry_watcher(symbol)
                return
            
            # Validate re-entry conditions
            validation_result = await self._validate_reentry_conditions(symbol, original_signal, entry_price)
            
            if not validation_result["valid"]:
                log_message = f"🔄 [Re-entry] Re-entry validation failed for {symbol}: {validation_result['reason']}"
                if group_name:
                    await send_telegram_log(log_message, group_name=group_name, tag="reentry")
                else:
                    await send_telegram_log(log_message, tag="reentry")
                logger.info(f"[Re-entry] Validation failed for {symbol}: {validation_result['reason']}")
                await self.cancel_reentry_watcher(symbol)
                return
            
            # Execute re-entry
            success = await self._execute_reentry(symbol, original_signal, validation_result["current_price"], group_name)
            
            if success:
                # Increment attempt counter
                self.reentry_attempts[symbol] = current_attempts + 1
                
                log_message = f"🔄 [Re-entry] Successfully re-entered {symbol} @ {validation_result['current_price']:,.2f} (attempt {current_attempts + 1}/{self.max_attempts})"
                if group_name:
                    await send_telegram_log(log_message, group_name=group_name, tag="reentry")
                else:
                    await send_telegram_log(log_message, tag="reentry")
                
                logger.info(f"[Re-entry] Successfully re-entered {symbol} (attempt {current_attempts + 1}/{self.max_attempts})")
                
                # Cancel re-entry watcher after successful re-entry
                await self.cancel_reentry_watcher(symbol)
            else:
                log_message = f"🔄 [Re-entry] Failed to re-enter {symbol} (attempt {current_attempts + 1}/{self.max_attempts})"
                if group_name:
                    await send_telegram_log(log_message, group_name=group_name, tag="reentry")
                else:
                    await send_telegram_log(log_message, tag="reentry")
                
                logger.error(f"[Re-entry] Failed to re-enter {symbol}")
                
                # If this was the last attempt, cancel the watcher
                if current_attempts + 1 >= self.max_attempts:
                    await self.cancel_reentry_watcher(symbol)
            
        except Exception as e:
            logger.error(f"❌ Error attempting re-entry for {symbol}: {e}")
    
    async def _is_symbol_blacklisted(self, symbol: str) -> bool:
        """Check if symbol is blacklisted."""
        try:
            from config.settings import OverrideConfig
            return symbol in OverrideConfig.BLOCKED_SYMBOLS
        except Exception as e:
            logger.error(f"❌ Error checking blacklist for {symbol}: {e}")
            return False
    
    async def _validate_reentry_conditions(self, symbol: str, original_signal: dict, 
                                         entry_price: float) -> dict:
        """
        Validate re-entry conditions.
        
        Returns:
            dict with validation result and current price
        """
        try:
            # Get current price
            current_price = await self._get_current_price(symbol)
            if current_price is None:
                return {"valid": False, "reason": "Unable to get current price"}
            
            # Check price deviation
            price_deviation = abs((current_price - entry_price) / entry_price) * 100
            if price_deviation > self.price_deviation:
                return {
                    "valid": False, 
                    "reason": f"Price deviation too high: {price_deviation:.2f}% > {self.price_deviation}%",
                    "current_price": current_price
                }
            
            # Check if signal structure is still valid
            if not self._is_signal_structure_valid(original_signal):
                return {
                    "valid": False, 
                    "reason": "Original signal structure is no longer valid",
                    "current_price": current_price
                }
            
            # Check if trade conditions still meet risk rules
            if not await self._validate_risk_conditions(symbol, original_signal, current_price):
                return {
                    "valid": False, 
                    "reason": "Trade conditions no longer meet risk rules",
                    "current_price": current_price
                }
            
            return {"valid": True, "current_price": current_price}
            
        except Exception as e:
            logger.error(f"❌ Error validating re-entry conditions for {symbol}: {e}")
            return {"valid": False, "reason": f"Validation error: {e}"}
    
    def _is_signal_structure_valid(self, signal: dict) -> bool:
        """Check if signal structure is still valid for re-entry."""
        try:
            required_fields = ["symbol", "side", "entry", "sl", "tp"]
            for field in required_fields:
                if field not in signal or signal[field] is None:
                    return False
            
            # Check if entry is a list or single value
            if isinstance(signal["entry"], list):
                if len(signal["entry"]) == 0:
                    return False
            elif not isinstance(signal["entry"], (int, float)):
                return False
            
            # Check if TP is a list
            if not isinstance(signal["tp"], list) or len(signal["tp"]) == 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking signal structure: {e}")
            return False
    
    async def _validate_risk_conditions(self, symbol: str, signal: dict, current_price: float) -> bool:
        """Validate that trade conditions still meet risk rules."""
        try:
            # Check if SL is reasonable
            sl_price = signal.get("sl")
            if sl_price is None:
                return False
            
            # Calculate SL distance
            if signal["side"].upper() == "LONG":
                sl_distance = ((current_price - sl_price) / current_price) * 100
            else:
                sl_distance = ((sl_price - current_price) / current_price) * 100
            
            # Check if SL distance is within reasonable bounds (0.5% to 5%)
            if sl_distance < 0.5 or sl_distance > 5.0:
                return False
            
            # Check if leverage is reasonable
            leverage = signal.get("leverage", TradingConfig.DEFAULT_LEVERAGE)
            if leverage > TradingConfig.LEVERAGE_CAP:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating risk conditions for {symbol}: {e}")
            return False
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol."""
        try:
            # Placeholder - would get from WebSocket or API
            # In real implementation, this would get the current market price
            return None
        except Exception as e:
            logger.error(f"❌ Error getting current price for {symbol}: {e}")
            return None
    
    async def _execute_reentry(self, symbol: str, original_signal: dict, 
                             current_price: float, group_name: str = None) -> bool:
        """Execute re-entry by placing orders."""
        try:
            # Update signal with current price
            reentry_signal = original_signal.copy()
            
            # Update entry price to current price
            if isinstance(reentry_signal["entry"], list):
                reentry_signal["entry"] = [current_price]
            else:
                reentry_signal["entry"] = current_price
            
            # Add re-entry metadata
            reentry_signal["is_reentry"] = True
            reentry_signal["reentry_attempt"] = self.reentry_attempts.get(symbol, 0) + 1
            reentry_signal["original_entry_price"] = self.entry_prices.get(symbol, current_price)
            
            # Execute re-entry using existing entry logic
            success = await handle_entry_signal(reentry_signal)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error executing re-entry for {symbol}: {e}")
            return False
    
    async def cancel_reentry_watcher(self, symbol: str):
        """Cancel re-entry watcher for a specific symbol."""
        if symbol in self.reentry_tasks:
            task = self.reentry_tasks[symbol]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Clean up
            del self.reentry_tasks[symbol]
            if symbol in self.reentry_active:
                del self.reentry_active[symbol]
            if symbol in self.reentry_attempts:
                del self.reentry_attempts[symbol]
            if symbol in self.original_signals:
                del self.original_signals[symbol]
            if symbol in self.entry_prices:
                del self.entry_prices[symbol]
            
            logger.info(f"[Re-entry] Watcher cancelled for {symbol}")
    
    async def cancel_all_reentry_watchers(self):
        """Cancel all active re-entry watchers."""
        for symbol in list(self.reentry_tasks.keys()):
            await self.cancel_reentry_watcher(symbol)
        
        logger.info("[Re-entry] All watchers cancelled")
    
    def is_reentry_active(self, symbol: str) -> bool:
        """Check if re-entry is active for a symbol."""
        return self.reentry_active.get(symbol, False)
    
    def get_reentry_attempts(self, symbol: str) -> int:
        """Get number of re-entry attempts for a symbol."""
        return self.reentry_attempts.get(symbol, 0)
    
    def get_reentry_progress(self, symbol: str) -> dict:
        """Get re-entry progress for a symbol."""
        attempts = self.get_reentry_attempts(symbol)
        return {
            "attempts": attempts,
            "max_attempts": self.max_attempts,
            "remaining_attempts": self.max_attempts - attempts,
            "is_active": self.is_reentry_active(symbol)
        }

# Global re-entry watcher instance
reentry_watcher = ReentryWatcher()

# Convenience functions
async def start_reentry_watcher(symbol: str, original_signal: dict, 
                              entry_price: float, exit_reason: str, group_name: str = None):
    """Start re-entry watcher for a closed trade."""
    await reentry_watcher.start_reentry_watcher(symbol, original_signal, entry_price, exit_reason, group_name)

async def cancel_reentry_watcher(symbol: str):
    """Cancel re-entry watcher for a trade."""
    await reentry_watcher.cancel_reentry_watcher(symbol)

async def cancel_all_reentry_watchers():
    """Cancel all active re-entry watchers."""
    await reentry_watcher.cancel_all_reentry_watchers()

def is_reentry_active(symbol: str) -> bool:
    """Check if re-entry is active for a symbol."""
    return reentry_watcher.is_reentry_active(symbol)

def get_reentry_attempts(symbol: str) -> int:
    """Get number of re-entry attempts for a symbol."""
    return reentry_watcher.get_reentry_attempts(symbol)

def get_reentry_progress(symbol: str) -> dict:
    """Get re-entry progress for a symbol."""
    return reentry_watcher.get_reentry_progress(symbol) 
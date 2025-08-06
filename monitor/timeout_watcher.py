# timeout_watcher.py – Automatic trade exit after timeout

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from config.settings import TradingConfig
from logic.exit import exit_trade
from utils.telegram_logger import send_telegram_log
from core.api import get_position

logger = logging.getLogger(__name__)

class TimeoutWatcher:
    """Manages automatic trade exit after timeout."""
    
    def __init__(self):
        self.timeout_tasks: Dict[str, asyncio.Task] = {}
        self.trade_start_times: Dict[str, datetime] = {}
        self.timeout_seconds = TradingConfig.AUTO_CLOSE_TIMEOUT
        logger.info(f"⏰ TimeoutWatcher initialized with {self.timeout_seconds}s timeout")
    
    async def start_timeout_for_trade(self, symbol: str, side: str, group_name: str = None):
        """Start a timeout timer for a new trade."""
        try:
            await self.cancel_timeout_for_symbol(symbol)
            
            self.trade_start_times[symbol] = datetime.now()
            
            timeout_task = asyncio.create_task(
                self._timeout_handler(symbol, side, group_name),
                name=f"timeout_{symbol}"
            )
            
            self.timeout_tasks[symbol] = timeout_task
            
            timeout_hours = self.timeout_seconds / 3600
            log_message = f"⏰ Auto-close timer started for {symbol} (timeout: {timeout_hours:.1f}h)"
            
            if group_name:
                await send_telegram_log(log_message, group_name=group_name, tag="timeout")
            else:
                await send_telegram_log(log_message, tag="timeout")
            
            logger.info(f"[Auto-Close] Timer started for {symbol} (timeout: {timeout_hours:.1f}h)")
            
        except Exception as e:
            logger.error(f"❌ Failed to start timeout for {symbol}: {e}")
    
    async def _timeout_handler(self, symbol: str, side: str, group_name: str = None):
        """Handle timeout for a specific symbol."""
        try:
            await asyncio.sleep(self.timeout_seconds)
            
            if await self._is_position_still_open(symbol):
                log_message = f"⏰ {symbol} still open after timeout — exiting position"
                
                if group_name:
                    await send_telegram_log(log_message, group_name=group_name, tag="timeout")
                else:
                    await send_telegram_log(log_message, tag="timeout")
                
                logger.info(f"[Auto-Close] {symbol} still open after timeout — exiting position")
                await self._exit_trade_async(symbol, side, group_name)
            else:
                logger.info(f"[Auto-Close] {symbol} position already closed before timeout")
                
        except asyncio.CancelledError:
            logger.info(f"[Auto-Close] Timeout task cancelled for {symbol} (position closed early)")
        except Exception as e:
            logger.error(f"❌ Error in timeout handler for {symbol}: {e}")
    
    async def _is_position_still_open(self, symbol: str) -> bool:
        """Check if a position is still open."""
        try:
            position = get_position(symbol)
            if position and float(position.get('total', 0)) != 0:
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error checking position status for {symbol}: {e}")
            return False
    
    async def _exit_trade_async(self, symbol: str, side: str, group_name: str = None):
        """Asynchronously exit a trade."""
        try:
            exit_trade(symbol, side)
            
            log_message = f"✅ Auto-closed {symbol} position after timeout"
            
            if group_name:
                await send_telegram_log(log_message, group_name=group_name, tag="timeout")
            else:
                await send_telegram_log(log_message, tag="timeout")
            
            logger.info(f"[Auto-Close] Successfully closed {symbol} position after timeout")
            
        except Exception as e:
            error_message = f"❌ Failed to auto-close {symbol} position: {e}"
            logger.error(f"[Auto-Close] {error_message}")
            
            if group_name:
                await send_telegram_log(error_message, group_name=group_name, tag="error")
            else:
                await send_telegram_log(error_message, tag="error")
    
    async def cancel_timeout_for_symbol(self, symbol: str):
        """Cancel timeout task for a specific symbol."""
        if symbol in self.timeout_tasks:
            task = self.timeout_tasks[symbol]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            del self.timeout_tasks[symbol]
            if symbol in self.trade_start_times:
                del self.trade_start_times[symbol]
            
            logger.info(f"[Auto-Close] Timeout task cancelled for {symbol} (position closed early)")
    
    async def cancel_all_timeouts(self):
        """Cancel all active timeout tasks."""
        for symbol in list(self.timeout_tasks.keys()):
            await self.cancel_timeout_for_symbol(symbol)
        
        logger.info("[Auto-Close] All timeout tasks cancelled")

# Global timeout watcher instance
timeout_watcher = TimeoutWatcher()

# Convenience functions
async def start_trade_timeout(symbol: str, side: str, group_name: str = None):
    """Start timeout for a new trade."""
    await timeout_watcher.start_timeout_for_trade(symbol, side, group_name)

async def cancel_trade_timeout(symbol: str):
    """Cancel timeout for a trade."""
    await timeout_watcher.cancel_timeout_for_symbol(symbol)

async def cancel_all_trade_timeouts():
    """Cancel all active trade timeouts."""
    await timeout_watcher.cancel_all_timeouts() 
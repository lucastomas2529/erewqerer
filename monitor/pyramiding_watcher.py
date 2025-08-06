# pyramiding_watcher.py – Dynamic pyramiding functionality

import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime
from config.settings import TradingConfig
from utils.telegram_logger import send_telegram_log
from core.api import get_position, place_market_order
from core.symbol_data import get_symbol_precision
from utils.quantity import calculate_quantity

logger = logging.getLogger(__name__)

class PyramidingWatcher:
    """
    Monitors trades and adds to winning positions when profit thresholds are reached.
    Implements pyramiding logic with configurable steps and risk management.
    """
    
    def __init__(self):
        self.pyramiding_tasks: Dict[str, asyncio.Task] = {}
        self.pyramiding_active: Dict[str, bool] = {}
        self.pyramid_steps_completed: Dict[str, List[int]] = {}  # symbol -> list of completed step indices
        self.entry_prices: Dict[str, float] = {}
        self.original_quantities: Dict[str, float] = {}
        self.sides: Dict[str, str] = {}
        self.max_steps = TradingConfig.MAX_PYRAMID_STEPS
        self.pol_thresholds = TradingConfig.PYRAMID_POL_THRESHOLDS
        self.step_size = TradingConfig.PYRAMID_STEP_SIZE
        self.min_pol = TradingConfig.PYRAMID_MIN_POL
        self.max_price_deviation = TradingConfig.PYRAMID_MAX_PRICE_DEVIATION
        logger.info(f"🔺 PyramidingWatcher initialized with {self.max_steps} max steps, thresholds: {self.pol_thresholds}%")
    
    async def start_pyramiding_watcher(self, symbol: str, entry_price: float, side: str, 
                                     original_quantity: float, group_name: str = None):
        """
        Start pyramiding watcher for a trade.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the trade
            side: Trade side ('long' or 'short')
            original_quantity: Original position quantity
            group_name: Optional group name for logging
        """
        try:
            # Cancel existing pyramiding task if any
            await self.cancel_pyramiding_watcher(symbol)
            
            # Initialize pyramiding state
            self.pyramiding_active[symbol] = True
            self.pyramid_steps_completed[symbol] = []
            self.entry_prices[symbol] = entry_price
            self.original_quantities[symbol] = original_quantity
            self.sides[symbol] = side
            
            # Create pyramiding task
            pyramiding_task = asyncio.create_task(
                self._pyramiding_handler(symbol, entry_price, side, original_quantity, group_name),
                name=f"pyramiding_{symbol}"
            )
            
            self.pyramiding_tasks[symbol] = pyramiding_task
            
            log_message = f"🔺 Pyramiding watcher started for {symbol} (max steps: {self.max_steps}, thresholds: {self.pol_thresholds}%)"
            
            if group_name:
                await send_telegram_log(log_message, group_name=group_name, tag="pyramiding")
            else:
                await send_telegram_log(log_message, tag="pyramiding")
            
            logger.info(f"[Pyramiding] Watcher started for {symbol} (max steps: {self.max_steps}, thresholds: {self.pol_thresholds}%)")
            
        except Exception as e:
            logger.error(f"❌ Failed to start pyramiding watcher for {symbol}: {e}")
    
    async def _pyramiding_handler(self, symbol: str, entry_price: float, side: str, 
                                original_quantity: float, group_name: str = None):
        """
        Handle pyramiding monitoring for a specific symbol.
        """
        try:
            # Monitor until all pyramid steps are completed or trade is closed
            while self.pyramiding_active.get(symbol, False):
                # Check if position is still open
                if not await self._is_position_still_open(symbol):
                    logger.info(f"[Pyramiding] {symbol} position closed - stopping pyramiding")
                    break
                
                # Check if TP4 is hit (stop pyramiding)
                if await self._is_tp4_hit(symbol, entry_price, side):
                    logger.info(f"[Pyramiding] {symbol} TP4 hit - stopping pyramiding")
                    break
                
                # Get current price and calculate P&L
                current_price = await self._get_current_price(symbol)
                if current_price is None:
                    await asyncio.sleep(5)
                    continue
                
                # Calculate current P&L
                current_pol = self._calculate_pol(entry_price, current_price, side)
                
                # Check if pyramiding should be triggered
                pyramid_action = await self._should_trigger_pyramiding(symbol, current_pol, current_price, entry_price)
                
                if pyramid_action:
                    await self._execute_pyramid_step(symbol, pyramid_action, current_price, group_name)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except asyncio.CancelledError:
            logger.info(f"[Pyramiding] Watcher cancelled for {symbol} (trade closed early)")
        except Exception as e:
            logger.error(f"❌ Error in pyramiding handler for {symbol}: {e}")
    
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
    
    async def _is_tp4_hit(self, symbol: str, entry_price: float, side: str) -> bool:
        """Check if TP4 is hit (stop pyramiding)."""
        try:
            current_price = await self._get_current_price(symbol)
            if current_price is None:
                return False
            
            current_pol = self._calculate_pol(entry_price, current_price, side)
            tp4_level = TradingConfig.TP_LEVELS[3] if len(TradingConfig.TP_LEVELS) >= 4 else 10.0
            
            return current_pol >= tp4_level
            
        except Exception as e:
            logger.error(f"❌ Error checking TP4 for {symbol}: {e}")
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
    
    def _calculate_pol(self, entry_price: float, current_price: float, side: str) -> float:
        """Calculate current profit/loss percentage."""
        if side.lower() == "long":
            return ((current_price - entry_price) / entry_price) * 100
        else:
            return ((entry_price - current_price) / entry_price) * 100
    
    async def _should_trigger_pyramiding(self, symbol: str, current_pol: float, 
                                       current_price: float, entry_price: float) -> Optional[dict]:
        """
        Determine if pyramiding should be triggered.
        
        Returns:
            dict with step info if pyramiding should be triggered, None otherwise
        """
        try:
            # Check minimum PoL requirement
            if current_pol < self.min_pol:
                return None
            
            # Check price deviation (avoid chasing bad fills)
            price_deviation = abs((current_price - entry_price) / entry_price) * 100
            if price_deviation > self.max_price_deviation:
                logger.info(f"[Pyramiding] {symbol} price deviation too high: {price_deviation:.2f}% > {self.max_price_deviation}%")
                return None
            
            # Check completed steps
            completed_steps = self.pyramid_steps_completed.get(symbol, [])
            if len(completed_steps) >= self.max_steps:
                logger.info(f"[Pyramiding] {symbol} max pyramid steps reached: {len(completed_steps)} >= {self.max_steps}")
                return None
            
            # Check each threshold
            for i, threshold in enumerate(self.pol_thresholds):
                if i not in completed_steps and current_pol >= threshold:
                    return {
                        "step_index": i,
                        "threshold": threshold,
                        "current_pol": current_pol,
                        "step_size": self.step_size
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking pyramiding trigger for {symbol}: {e}")
            return None
    
    async def _execute_pyramid_step(self, symbol: str, pyramid_action: dict, 
                                  current_price: float, group_name: str = None):
        """Execute a pyramid step by adding to the position."""
        try:
            step_index = pyramid_action["step_index"]
            threshold = pyramid_action["threshold"]
            current_pol = pyramid_action["current_pol"]
            step_size = pyramid_action["step_size"]
            
            # Calculate pyramid quantity
            original_qty = self.original_quantities.get(symbol, 0)
            pyramid_qty = original_qty * step_size
            
            # Get symbol precision
            precision = get_symbol_precision(symbol)
            pyramid_qty = round(pyramid_qty, precision['quantity'])
            
            # Get side for order
            side = self.sides.get(symbol, "long")
            order_side = "buy" if side.lower() == "long" else "sell"
            
            # Place pyramid order
            success = await self._place_pyramid_order(symbol, order_side, pyramid_qty, current_price, group_name)
            
            if success:
                # Mark step as completed
                self.pyramid_steps_completed[symbol].append(step_index)
                
                # Log the pyramid step
                step_percentage = step_size * 100
                log_message = f"🔺 [Pyramiding] Added {step_percentage}% to {symbol} @ {current_price:,.2f} (PoL: {current_pol:.2f}% ≥ {threshold}%)"
                
                if group_name:
                    await send_telegram_log(log_message, group_name=group_name, tag="pyramiding")
                else:
                    await send_telegram_log(log_message, tag="pyramiding")
                
                logger.info(f"[Pyramiding] {symbol} step {step_index + 1} completed: +{step_percentage}% @ {current_price}")
                
                # Check if all steps completed
                if len(self.pyramid_steps_completed[symbol]) >= self.max_steps:
                    log_message = f"🔺 [Pyramiding] All {self.max_steps} pyramid steps completed for {symbol}"
                    if group_name:
                        await send_telegram_log(log_message, group_name=group_name, tag="pyramiding")
                    else:
                        await send_telegram_log(log_message, tag="pyramiding")
                    logger.info(f"[Pyramiding] {symbol} all steps completed")
            else:
                logger.error(f"[Pyramiding] Failed to execute pyramid step for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error executing pyramid step for {symbol}: {e}")
    
    async def _place_pyramid_order(self, symbol: str, side: str, quantity: float, 
                                 price: float, group_name: str = None) -> bool:
        """Place a pyramid order on the exchange."""
        try:
            # Place market order for pyramid
            success = place_market_order(symbol=symbol, side=side, size=quantity)
            
            if success:
                logger.info(f"[Pyramiding] Pyramid order placed: {symbol} {side} {quantity}")
                return True
            else:
                logger.error(f"[Pyramiding] Failed to place pyramid order: {symbol} {side} {quantity}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error placing pyramid order for {symbol}: {e}")
            return False
    
    async def cancel_pyramiding_watcher(self, symbol: str):
        """Cancel pyramiding watcher for a specific symbol."""
        if symbol in self.pyramiding_tasks:
            task = self.pyramiding_tasks[symbol]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Clean up
            del self.pyramiding_tasks[symbol]
            if symbol in self.pyramiding_active:
                del self.pyramiding_active[symbol]
            if symbol in self.pyramid_steps_completed:
                del self.pyramid_steps_completed[symbol]
            if symbol in self.entry_prices:
                del self.entry_prices[symbol]
            if symbol in self.original_quantities:
                del self.original_quantities[symbol]
            if symbol in self.sides:
                del self.sides[symbol]
            
            logger.info(f"[Pyramiding] Watcher cancelled for {symbol}")
    
    async def cancel_all_pyramiding_watchers(self):
        """Cancel all active pyramiding watchers."""
        for symbol in list(self.pyramiding_tasks.keys()):
            await self.cancel_pyramiding_watcher(symbol)
        
        logger.info("[Pyramiding] All watchers cancelled")
    
    def is_pyramiding_active(self, symbol: str) -> bool:
        """Check if pyramiding is active for a symbol."""
        return self.pyramiding_active.get(symbol, False)
    
    def get_completed_pyramid_steps(self, symbol: str) -> List[int]:
        """Get completed pyramid steps for a symbol."""
        return self.pyramid_steps_completed.get(symbol, [])
    
    def get_pyramid_progress(self, symbol: str) -> dict:
        """Get pyramiding progress for a symbol."""
        completed_steps = self.get_completed_pyramid_steps(symbol)
        return {
            "completed_steps": completed_steps,
            "total_steps": self.max_steps,
            "remaining_steps": self.max_steps - len(completed_steps),
            "is_active": self.is_pyramiding_active(symbol)
        }

# Global pyramiding watcher instance
pyramiding_watcher = PyramidingWatcher()

# Convenience functions
async def start_pyramiding_watcher(symbol: str, entry_price: float, side: str, 
                                 original_quantity: float, group_name: str = None):
    """Start pyramiding watcher for a trade."""
    await pyramiding_watcher.start_pyramiding_watcher(symbol, entry_price, side, original_quantity, group_name)

async def cancel_pyramiding_watcher(symbol: str):
    """Cancel pyramiding watcher for a trade."""
    await pyramiding_watcher.cancel_pyramiding_watcher(symbol)

async def cancel_all_pyramiding_watchers():
    """Cancel all active pyramiding watchers."""
    await pyramiding_watcher.cancel_all_pyramiding_watchers()

def is_pyramiding_active(symbol: str) -> bool:
    """Check if pyramiding is active for a symbol."""
    return pyramiding_watcher.is_pyramiding_active(symbol)

def get_completed_pyramid_steps(symbol: str) -> List[int]:
    """Get completed pyramid steps for a symbol."""
    return pyramiding_watcher.get_completed_pyramid_steps(symbol)

def get_pyramid_progress(symbol: str) -> dict:
    """Get pyramiding progress for a symbol."""
    return pyramiding_watcher.get_pyramid_progress(symbol) 
# trade_state.py – håller aktuell status för varje trade
from dataclasses import dataclass, field
from typing import Optional
# Lazy imports to avoid circular dependencies
# from monitor.timeout_watcher import start_trade_timeout, cancel_trade_timeout
# from monitor.breakeven_ws import start_breakeven_watcher, cancel_breakeven_watcher
# from monitor.trailing import start_trailing_watcher, cancel_trailing_watcher
# from monitor.pyramiding_watcher import start_pyramiding_watcher, cancel_pyramiding_watcher
# from monitor.reentry_watcher import start_reentry_watcher, cancel_reentry_watcher


@dataclass
class TradeState:
    symbol: str
    side: str  # "LONG" eller "SHORT"
    entry_price: float
    sl_price: Optional[float]
    leverage: float
    initial_margin: float
    quantity: float
    current_pol: float = 0.0
    trailing_active: bool = False
    tp_hits: list = field(default_factory=list)
    sl_updated: bool = False
    position_active: bool = True
    timeout_started: bool = False  # Track if timeout has been started
    breakeven_started: bool = False  # Track if break-even watcher has been started
    breakeven_triggered: bool = False  # Track if break-even was triggered
    trailing_started: bool = False  # Track if trailing watcher has been started
    trailing_active: bool = False  # Track if trailing is active
    pyramiding_started: bool = False  # Track if pyramiding watcher has been started
    pyramiding_active: bool = False  # Track if pyramiding is active
    pyramid_steps_completed: list = field(default_factory=list)  # Track completed pyramid steps
    reentry_attempts: int = 0  # Track re-entry attempts for this trade

    def update_pol(self, current_price: float) -> None:
        """
        Uppdatera aktuell profit/loss (i %) beroende på riktning.
        """
        if not self.entry_price:
            self.current_pol = 0.0
            return

        if self.side.upper() == "LONG":
            self.current_pol = ((current_price - self.entry_price) / self.entry_price) * 100
        else:
            self.current_pol = ((self.entry_price - current_price) / self.entry_price) * 100

    def mark_tp_hit(self, tp_level: float) -> None:
        """
        Lägg till en TP-nivå som träffats (om ej redan loggad).
        """
        if tp_level not in self.tp_hits:
            self.tp_hits.append(tp_level)

    def should_move_sl(self, current_price: float) -> Optional[float]:
        """
        Bestäm ny SL baserat på TP-nivåer eller fallback.
        """
        if self.current_pol >= 2.4 and self.sl_price < self.entry_price * 1.0015:
            return round(self.entry_price * 1.0015, 6)

        if len(self.tp_hits) >= 1 and not self.sl_updated:
            return self.tp_hits[0]  # t.ex. TP1

        return None

    def should_trigger_trailing(self) -> bool:
        """
        Avgör om trailing stop ska aktiveras.
        """
        return self.current_pol >= 6.0 or len(self.tp_hits) >= 4

    async def start_timeout(self, group_name: str = None):
        """
        Start timeout timer for this trade.
        """
        if not self.timeout_started and self.position_active:
            # Lazy import to avoid circular dependency
            from monitor.timeout_watcher import start_trade_timeout
            await start_trade_timeout(self.symbol, self.side.lower(), group_name)
            self.timeout_started = True

    async def cancel_timeout(self):
        """
        Cancel timeout timer for this trade (e.g., when position is closed early).
        """
        if self.timeout_started:
            # Lazy import to avoid circular dependency
            from monitor.timeout_watcher import cancel_trade_timeout
            await cancel_trade_timeout(self.symbol)
            self.timeout_started = False

    async def start_breakeven(self, group_name: str = None, tp_levels: list = None):
        """
        Start break-even watcher for this trade.
        """
        if not self.breakeven_started and self.position_active:
            # Lazy import to avoid circular dependency
            from monitor.breakeven_ws import start_breakeven_watcher
            await start_breakeven_watcher(
                self.symbol, 
                self.entry_price, 
                self.side.lower(), 
                group_name, 
                tp_levels
            )
            self.breakeven_started = True

    async def cancel_breakeven(self):
        """
        Cancel break-even watcher for this trade (e.g., when position is closed early).
        """
        if self.breakeven_started:
            # Lazy import to avoid circular dependency
            from monitor.breakeven_ws import cancel_breakeven_watcher
            await cancel_breakeven_watcher(self.symbol)
            self.breakeven_started = False

    async def start_trailing(self, group_name: str = None):
        """
        Start trailing watcher for this trade.
        """
        if not self.trailing_started and self.position_active:
            await start_trailing_watcher(
                self.symbol, 
                self.entry_price, 
                self.side.lower(), 
                self.sl_price,
                group_name
            )
            self.trailing_started = True

    async def cancel_trailing(self):
        """
        Cancel trailing watcher for this trade (e.g., when position is closed early).
        """
        if self.trailing_started:
            await cancel_trailing_watcher(self.symbol)
            self.trailing_started = False

    async def start_pyramiding(self, group_name: str = None):
        """
        Start pyramiding watcher for this trade.
        """
        if not self.pyramiding_started and self.position_active:
            await start_pyramiding_watcher(
                self.symbol, 
                self.entry_price, 
                self.side.lower(), 
                self.quantity,
                group_name
            )
            self.pyramiding_started = True

    async def cancel_pyramiding(self):
        """
        Cancel pyramiding watcher for this trade (e.g., when position is closed early).
        """
        if self.pyramiding_started:
            await cancel_pyramiding_watcher(self.symbol)
            self.pyramiding_started = False

    async def start_reentry(self, original_signal: dict, exit_reason: str, group_name: str = None):
        """
        Start re-entry watcher for this trade after it's closed.
        """
        if not self.pyramiding_started and self.position_active:
            await start_reentry_watcher(
                self.symbol, 
                original_signal,
                self.entry_price, 
                exit_reason,
                group_name
            )
            self.reentry_attempts += 1

    def reset(self) -> None:
        """
        Nollställ hela trade-status (t.ex. efter SL).
        """
        self.current_pol = 0.0
        self.trailing_active = False
        self.tp_hits.clear()
        self.sl_updated = False
        self.position_active = False
        self.timeout_started = False
        self.breakeven_started = False
        self.breakeven_triggered = False
        self.trailing_started = False
        self.trailing_active = False
        self.pyramiding_started = False
        self.pyramiding_active = False
        self.pyramid_steps_completed.clear()
        self.reentry_attempts = 0

# Global state instance for backward compatibility
state = {}  # Dictionary to hold multiple TradeState instances by symbol

async def monitor_pol_and_adjust(state, signal):
    """
    Monitor profit/loss and adjust positions accordingly.
    TODO: Implement actual P&L monitoring logic.
    """
    print(f"📊 Monitoring P&L for {signal.get('symbol', 'Unknown')}")
    return {"status": "monitoring"}

async def create_trade_state(symbol: str, side: str, entry_price: float, sl_price: float, 
                           leverage: float, initial_margin: float, quantity: float, 
                           group_name: str = None) -> TradeState:
    """
    Create a new trade state and start timeout timer.
    
    Args:
        symbol: Trading symbol
        side: Trade side (LONG/SHORT)
        entry_price: Entry price
        sl_price: Stop loss price
        leverage: Leverage used
        initial_margin: Initial margin
        quantity: Position quantity
        group_name: Optional group name for timeout logging
        
    Returns:
        TradeState instance with timeout started
    """
    trade_state = TradeState(
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        sl_price=sl_price,
        leverage=leverage,
        initial_margin=initial_margin,
        quantity=quantity
    )
    
    # Start timeout timer
    await trade_state.start_timeout(group_name)
    
    # Start break-even watcher
    tp_levels = signal.get("tp", []) if signal else None
    await trade_state.start_breakeven(group_name, tp_levels)
    
    # Start trailing watcher
    await trade_state.start_trailing(group_name)
    
    # Start pyramiding watcher
    await trade_state.start_pyramiding(group_name)
    
    # Store in global state
    state[symbol] = trade_state
    
    return trade_state

async def close_trade_state(symbol: str, group_name: str = None, exit_reason: str = "UNKNOWN", exit_price: float = None):
    """
    Close a trade state and cancel its timeout timer.
    
    Args:
        symbol: Trading symbol
        group_name: Optional group name for logging
        exit_reason: Reason for exit ("TP", "SL", "MANUAL", "TIMEOUT")
        exit_price: Exit price for reporting
    """
    if symbol in state:
        trade_state = state[symbol]
        
        # Generate trade report before closing
        try:
            from monitor.reporting import generate_trade_report
            if exit_price is None:
                exit_price = trade_state.entry_price  # Fallback to entry price
            
            await generate_trade_report(
                trade_state=trade_state,
                exit_price=exit_price,
                exit_reason=exit_reason,
                group_name=group_name
            )
            print(f"[REPORT] Trade report generated for {symbol}")
        except Exception as e:
            print(f"[REPORT] Failed to generate trade report for {symbol}: {e}")
        
        # Cancel timeout timer
        await trade_state.cancel_timeout()
        
        # Cancel break-even watcher
        await trade_state.cancel_breakeven()
        
        # Cancel trailing watcher
        await trade_state.cancel_trailing()
        
        # Cancel pyramiding watcher
        await trade_state.cancel_pyramiding()
        
        # Reset trade state
        trade_state.reset()
        
        # Remove from global state
        del state[symbol]
        
        print(f"✅ Trade state closed for {symbol}")
    else:
        print(f"⚠️ No trade state found for {symbol}")


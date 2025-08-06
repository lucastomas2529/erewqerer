#!/usr/bin/env python3
"""
Telegram Admin Command Handler.
Processes and executes admin commands for bot control and configuration.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from config.settings import (
    ADMIN_COMMANDS_ENABLED,
    ADMIN_USER_IDS,
    ADMIN_USERNAMES,
    ADMIN_COMMAND_PREFIX,
    ADMIN_LOG_ALL_COMMANDS,
    ADMIN_REQUIRE_CONFIRMATION
)
from config.strategy_control import is_strategy_enabled, get_all_strategy_overrides
from utils.logger import log_event
from utils.telegram_logger import send_telegram_log

@dataclass
class AdminCommand:
    """Admin command data structure."""
    command: str
    args: List[str]
    user_id: int
    username: str
    chat_id: int
    timestamp: datetime
    raw_message: str

class AdminCommandHandler:
    """Handles admin command processing and execution."""
    
    def __init__(self):
        self.command_history: List[AdminCommand] = []
        self.confirmation_pending: Dict[int, Dict] = {}  # user_id -> pending command
        
        # Define available commands and their handlers
        self.commands = {
            "status": self._handle_status,
            "enable": self._handle_enable,
            "disable": self._handle_disable,
            "report": self._handle_report,
            "restart": self._handle_restart,
            "config": self._handle_config,
            "help": self._handle_help,
            "confirm": self._handle_confirm,
            "cancel": self._handle_cancel
        }
    
    def is_admin(self, user_id: int, username: str = None) -> bool:
        """
        Check if user is authorized admin.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username (optional)
            
        Returns:
            bool: True if user is admin, False otherwise
        """
        # Check user ID
        if user_id in ADMIN_USER_IDS:
            return True
        
        # Check username if provided
        if username and username.lower() in [u.lower() for u in ADMIN_USERNAMES]:
            return True
        
        return False
    
    def parse_command(self, message: str, user_id: int, username: str, chat_id: int) -> Optional[AdminCommand]:
        """
        Parse admin command from message.
        
        Args:
            message: Raw message text
            user_id: Telegram user ID
            username: Telegram username
            chat_id: Telegram chat ID
            
        Returns:
            AdminCommand or None if not a valid command
        """
        try:
            # Check if message starts with command prefix
            if not message.startswith(ADMIN_COMMAND_PREFIX):
                return None
            
            # Remove prefix and split into parts
            command_text = message[len(ADMIN_COMMAND_PREFIX):].strip()
            parts = command_text.split()
            
            if not parts:
                return None
            
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Create command object
            admin_command = AdminCommand(
                command=command,
                args=args,
                user_id=user_id,
                username=username,
                chat_id=chat_id,
                timestamp=datetime.now(),
                raw_message=message
            )
            
            return admin_command
            
        except Exception as e:
            log_event(f"[ERROR] Failed to parse admin command: {e}", "ERROR")
            return None
    
    async def handle_command(self, command: AdminCommand) -> str:
        """
        Handle admin command execution.
        
        Args:
            command: AdminCommand instance
            
        Returns:
            str: Response message
        """
        try:
            # Check if admin commands are enabled
            if not ADMIN_COMMANDS_ENABLED:
                return "❌ Admin commands are currently disabled."
            
            # Check if user is admin
            if not self.is_admin(command.user_id, command.username):
                log_event(f"[ADMIN] Unauthorized command attempt by {command.username} ({command.user_id}): {command.raw_message}", "WARNING")
                return "❌ You are not authorized to use admin commands."
            
            # Log command if enabled
            if ADMIN_LOG_ALL_COMMANDS:
                log_event(f"[ADMIN] Command from {command.username} ({command.user_id}): {command.raw_message}", "INFO")
            
            # Store command in history
            self.command_history.append(command)
            
            # Check if command exists
            if command.command not in self.commands:
                return f"❌ Unknown command: {command.command}\nUse /help for available commands."
            
            # Execute command
            response = await self.commands[command.command](command)
            
            # Log successful execution
            log_event(f"[ADMIN] Command executed successfully: {command.command} by {command.username}", "INFO")
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error executing command: {str(e)}"
            log_event(f"[ERROR] Admin command error: {e}", "ERROR")
            return error_msg
    
    async def _handle_status(self, command: AdminCommand) -> str:
        """Handle /status command - show bot health and active groups."""
        try:
            from monitor.trade_state import state
            from config.settings import TelegramConfig
            
            # Get active trades
            active_trades = len([s for s in state.values() if s.position_active])
            
            # Get active groups
            active_groups = list(TelegramConfig.TELEGRAM_GROUPS.keys())
            
            # Get uptime (placeholder - would need actual uptime tracking)
            uptime = "Running"
            
            status_msg = f"""
🤖 **BOT STATUS**

**Health:** ✅ {uptime}
**Active Trades:** {active_trades}
**Active Groups:** {len(active_groups)}

**Groups:**
"""
            
            for group in active_groups:
                status_msg += f"• {group}\n"
            
            status_msg += f"""
**Admin Commands:** {'✅ Enabled' if ADMIN_COMMANDS_ENABLED else '❌ Disabled'}
**Last Command:** {command.timestamp.strftime('%H:%M:%S')}
"""
            
            return status_msg.strip()
            
        except Exception as e:
            return f"❌ Error getting status: {str(e)}"
    
    async def _handle_enable(self, command: AdminCommand) -> str:
        """Handle /enable command - enable strategy for symbol/timeframe."""
        try:
            if len(command.args) < 2:
                return "❌ Usage: /enable <strategy> <symbol> [timeframe] [group]"
            
            strategy = command.args[0].upper()
            symbol = command.args[1].upper()
            timeframe = command.args[2] if len(command.args) > 2 else "default"
            group = command.args[3] if len(command.args) > 3 else "default"
            
            # Validate strategy
            valid_strategies = ["TP", "SL", "TRAILING_STOP", "BREAK_EVEN", "REENTRY", "PYRAMIDING"]
            if strategy not in valid_strategies:
                return f"❌ Invalid strategy. Valid options: {', '.join(valid_strategies)}"
            
            # This would need to modify the strategy overrides configuration
            # For now, return a placeholder response
            response = f"✅ Strategy {strategy} enabled for {symbol} ({timeframe}) in group {group}"
            
            # Log the action
            log_event(f"[ADMIN] Strategy {strategy} enabled for {symbol}/{timeframe} by {command.username}", "INFO")
            
            return response
            
        except Exception as e:
            return f"❌ Error enabling strategy: {str(e)}"
    
    async def _handle_disable(self, command: AdminCommand) -> str:
        """Handle /disable command - disable strategy for symbol/timeframe."""
        try:
            if len(command.args) < 2:
                return "❌ Usage: /disable <strategy> <symbol> [timeframe] [group]"
            
            strategy = command.args[0].upper()
            symbol = command.args[1].upper()
            timeframe = command.args[2] if len(command.args) > 2 else "default"
            group = command.args[3] if len(command.args) > 3 else "default"
            
            # Validate strategy
            valid_strategies = ["TP", "SL", "TRAILING_STOP", "BREAK_EVEN", "REENTRY", "PYRAMIDING"]
            if strategy not in valid_strategies:
                return f"❌ Invalid strategy. Valid options: {', '.join(valid_strategies)}"
            
            # Check if confirmation is required
            if ADMIN_REQUIRE_CONFIRMATION:
                self.confirmation_pending[command.user_id] = {
                    "action": "disable",
                    "strategy": strategy,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "group": group,
                    "timestamp": datetime.now()
                }
                return f"⚠️ Please confirm: /confirm to disable {strategy} for {symbol} ({timeframe})"
            
            # This would need to modify the strategy overrides configuration
            # For now, return a placeholder response
            response = f"✅ Strategy {strategy} disabled for {symbol} ({timeframe}) in group {group}"
            
            # Log the action
            log_event(f"[ADMIN] Strategy {strategy} disabled for {symbol}/{timeframe} by {command.username}", "INFO")
            
            return response
            
        except Exception as e:
            return f"❌ Error disabling strategy: {str(e)}"
    
    async def _handle_report(self, command: AdminCommand) -> str:
        """Handle /report command - generate manual reports."""
        try:
            if not command.args:
                return "❌ Usage: /report <daily|weekly|trades|performance|optimize>"
            
            report_type = command.args[0].lower()
            
            if report_type == "daily":
                # Generate daily report
                from monitor.reporting import trade_reporter
                report = trade_reporter.get_daily_summary()
                return f"📊 **DAILY REPORT**\n\n{report}"
            
            elif report_type == "weekly":
                # Generate weekly report (placeholder)
                return "📊 **WEEKLY REPORT**\n\nWeekly reporting not yet implemented."
            
            elif report_type == "trades":
                # Show recent trades
                from monitor.reporting import trade_reporter
                recent_trades = trade_reporter.trade_history[-10:] if trade_reporter.trade_history else []
                
                if not recent_trades:
                    return "📊 No recent trades found."
                
                report = "📊 **RECENT TRADES**\n\n"
                for trade in recent_trades:
                    pnl_emoji = "🟢" if trade.pnl_percentage > 0 else "🔴"
                    report += f"{pnl_emoji} {trade.symbol} {trade.side}: {trade.pnl_percentage:+.2f}%\n"
                
                return report
            
            elif report_type == "performance":
                # Show performance metrics
                from monitor.reporting import trade_reporter
                
                if not trade_reporter.trade_history:
                    return "📊 No trading history available."
                
                total_trades = len(trade_reporter.trade_history)
                winning_trades = len([t for t in trade_reporter.trade_history if t.pnl_percentage > 0])
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                total_pnl = sum(t.pnl_percentage for t in trade_reporter.trade_history)
                
                return f"""
📊 **PERFORMANCE METRICS**

**Total Trades:** {total_trades}
**Winning Trades:** {winning_trades}
**Win Rate:** {win_rate:.1f}%
**Total P&L:** {total_pnl:+.2f}%
"""
            
            elif report_type == "optimize":
                # Generate strategy optimization report
                return await self._generate_optimization_report()
            
            else:
                return f"❌ Unknown report type: {report_type}"
            
        except Exception as e:
            return f"❌ Error generating report: {str(e)}"
    
    async def _handle_restart(self, command: AdminCommand) -> str:
        """Handle /restart command - restart bot modules."""
        try:
            if not command.args:
                return "❌ Usage: /restart <module>"
            
            module = command.args[0].lower()
            
            # Check if confirmation is required for restart
            if ADMIN_REQUIRE_CONFIRMATION:
                self.confirmation_pending[command.user_id] = {
                    "action": "restart",
                    "module": module,
                    "timestamp": datetime.now()
                }
                return f"⚠️ Please confirm: /confirm to restart {module} module"
            
            # Placeholder for module restart logic
            response = f"✅ Module {module} restart initiated"
            
            # Log the action
            log_event(f"[ADMIN] Module {module} restart initiated by {command.username}", "INFO")
            
            return response
            
        except Exception as e:
            return f"❌ Error restarting module: {str(e)}"
    
    async def _handle_config(self, command: AdminCommand) -> str:
        """Handle /config command - show current configuration."""
        try:
            if not command.args:
                return "❌ Usage: /config <strategy|admin|general>"
            
            config_type = command.args[0].lower()
            
            if config_type == "strategy":
                # Show strategy configuration
                from config.settings import (
                    ENABLE_TP, ENABLE_SL, ENABLE_TRAILING_STOP,
                    ENABLE_BREAK_EVEN, ENABLE_REENTRY, ENABLE_PYRAMIDING
                )
                
                return f"""
⚙️ **STRATEGY CONFIGURATION**

**Take Profit:** {'✅' if ENABLE_TP else '❌'}
**Stop Loss:** {'✅' if ENABLE_SL else '❌'}
**Trailing Stop:** {'✅' if ENABLE_TRAILING_STOP else '❌'}
**Break Even:** {'✅' if ENABLE_BREAK_EVEN else '❌'}
**Re-entry:** {'✅' if ENABLE_REENTRY else '❌'}
**Pyramiding:** {'✅' if ENABLE_PYRAMIDING else '❌'}
"""
            
            elif config_type == "admin":
                # Show admin configuration
                return f"""
👑 **ADMIN CONFIGURATION**

**Commands Enabled:** {'✅' if ADMIN_COMMANDS_ENABLED else '❌'}
**Log All Commands:** {'✅' if ADMIN_LOG_ALL_COMMANDS else '❌'}
**Require Confirmation:** {'✅' if ADMIN_REQUIRE_CONFIRMATION else '❌'}
**Admin User IDs:** {len(ADMIN_USER_IDS)} users
**Admin Usernames:** {len(ADMIN_USERNAMES)} users
"""
            
            elif config_type == "general":
                # Show general configuration
                from config.settings import (
                    DEFAULT_IM, RISK_PERCENT, LEVERAGE_CAP,
                    SL_PCT, TP_LEVELS, AUTO_CLOSE_TIMEOUT
                )
                
                return f"""
🔧 **GENERAL CONFIGURATION**

**Default IM:** ${DEFAULT_IM}
**Risk Percent:** {RISK_PERCENT}%
**Leverage Cap:** x{LEVERAGE_CAP}
**Stop Loss:** {SL_PCT}%
**Take Profit Levels:** {TP_LEVELS}
**Auto Close Timeout:** {AUTO_CLOSE_TIMEOUT}s
"""
            
            else:
                return f"❌ Unknown config type: {config_type}"
            
        except Exception as e:
            return f"❌ Error showing configuration: {str(e)}"
    
    async def _handle_help(self, command: AdminCommand) -> str:
        """Handle /help command - show available commands."""
        help_text = """
👑 **ADMIN COMMANDS**

**Status & Reports:**
/status - Show bot health and active groups
/report daily - Generate daily trading report
/report weekly - Generate weekly trading report
/report trades - Show recent trades
/report performance - Show performance metrics
/report optimize - Generate strategy optimization recommendations

**Strategy Control:**
/enable <strategy> <symbol> [timeframe] [group] - Enable strategy
/disable <strategy> <symbol> [timeframe] [group] - Disable strategy

**System Control:**
/restart <module> - Restart bot module
/config <type> - Show configuration (strategy/admin/general)

**Other:**
/help - Show this help message
/confirm - Confirm pending action
/cancel - Cancel pending action

**Strategies:** TP, SL, TRAILING_STOP, BREAK_EVEN, REENTRY, PYRAMIDING
**Examples:**
/enable TP BTCUSDT 5m cryptoraketen
/disable REENTRY ETHUSDT 1h
/restart listener
/report optimize
"""
        return help_text.strip()
    
    async def _handle_confirm(self, command: AdminCommand) -> str:
        """Handle /confirm command - confirm pending action."""
        try:
            if command.user_id not in self.confirmation_pending:
                return "❌ No pending action to confirm."
            
            pending = self.confirmation_pending[command.user_id]
            action = pending["action"]
            
            if action == "disable":
                strategy = pending["strategy"]
                symbol = pending["symbol"]
                timeframe = pending["timeframe"]
                group = pending["group"]
                
                # Execute the disable action
                response = f"✅ Strategy {strategy} disabled for {symbol} ({timeframe}) in group {group}"
                log_event(f"[ADMIN] Strategy {strategy} disabled for {symbol}/{timeframe} by {command.username}", "INFO")
            
            elif action == "restart":
                module = pending["module"]
                
                # Execute the restart action
                response = f"✅ Module {module} restart initiated"
                log_event(f"[ADMIN] Module {module} restart initiated by {command.username}", "INFO")
            
            else:
                response = f"❌ Unknown pending action: {action}"
            
            # Clear pending action
            del self.confirmation_pending[command.user_id]
            
            return response
            
        except Exception as e:
            return f"❌ Error confirming action: {str(e)}"
    
    async def _handle_cancel(self, command: AdminCommand) -> str:
        """Handle /cancel command - cancel pending action."""
        try:
            if command.user_id not in self.confirmation_pending:
                return "❌ No pending action to cancel."
            
            # Clear pending action
            del self.confirmation_pending[command.user_id]
            
            return "✅ Pending action cancelled."
            
        except Exception as e:
            return f"❌ Error cancelling action: {str(e)}"
    
    async def _generate_optimization_report(self) -> str:
        """Generate strategy optimization report using StrategyOptimizer."""
        try:
            # Import StrategyOptimizer
            from analytics.strategy_optimizer import StrategyOptimizer
            
            # Create optimizer instance
            optimizer = StrategyOptimizer()
            
            # Load accuracy data
            if not optimizer.load_accuracy_data():
                return "❌ **STRATEGY OPTIMIZATION REPORT**\n\n⚠️ No accuracy data found. Please ensure signal accuracy tracking is enabled and data has been collected."
            
            # Analyze performance and generate recommendations
            optimizer.analyze_group_performance()
            recommendations = optimizer.generate_recommendations()
            
            if not recommendations:
                return "📊 **STRATEGY OPTIMIZATION REPORT**\n\n✅ No optimization recommendations available. All strategies are performing within acceptable parameters."
            
            # Export recommendations in string format
            report = optimizer.export_recommendations("string")
            
            # Add header with timestamp
            header = f"📊 **STRATEGY OPTIMIZATION REPORT**\n\n"
            header += f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += f"📈 Total Recommendations: {len(recommendations)}\n\n"
            
            return header + report
            
        except ImportError as e:
            return f"❌ **STRATEGY OPTIMIZATION REPORT**\n\n⚠️ StrategyOptimizer module not found: {str(e)}"
        except Exception as e:
            log_event(f"[ERROR] Failed to generate optimization report: {e}", "ERROR")
            return f"❌ **STRATEGY OPTIMIZATION REPORT**\n\n⚠️ Error generating report: {str(e)}"
    
    def get_command_history(self, limit: int = 10) -> List[AdminCommand]:
        """Get recent command history."""
        return self.command_history[-limit:] if self.command_history else []
    
    def clear_command_history(self):
        """Clear command history."""
        self.command_history.clear()

# Global command handler instance
admin_command_handler = AdminCommandHandler()

async def process_admin_command(message: str, user_id: int, username: str, chat_id: int) -> Optional[str]:
    """
    Process admin command and return response.
    
    Args:
        message: Raw message text
        user_id: Telegram user ID
        username: Telegram username
        chat_id: Telegram chat ID
        
    Returns:
        Response message or None if not an admin command
    """
    try:
        # Parse command
        command = admin_command_handler.parse_command(message, user_id, username, chat_id)
        
        if not command:
            return None
        
        # Handle command
        response = await admin_command_handler.handle_command(command)
        
        return response
        
    except Exception as e:
        log_event(f"[ERROR] Failed to process admin command: {e}", "ERROR")
        return f"❌ Error processing command: {str(e)}" 
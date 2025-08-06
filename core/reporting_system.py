#!/usr/bin/env python3
"""
Comprehensive logging and reporting system for trading bot.
Tracks all activities and generates detailed reports.
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import os

from config.settings import TradingConfig
from utils.telegram_logger import send_telegram_log
from utils.logger import log_event

@dataclass
class TradeRecord:
    """Data class for trade records."""
    id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    entry_price: float
    exit_price: Optional[float]
    sl_price: Optional[float]
    tp_prices: List[float]
    order_ids: List[str]
    group_name: str
    signal_source: str
    entry_time: datetime
    exit_time: Optional[datetime]
    pnl: Optional[float]
    pnl_percentage: Optional[float]
    status: str  # 'open', 'closed', 'cancelled'
    close_reason: Optional[str]  # 'tp', 'sl', 'manual', 'timeout'
    processing_time: float
    admin_command: bool = False

@dataclass
class SignalRecord:
    """Data class for signal records."""
    id: str
    group_name: str
    signal_text: str
    parsed_data: Dict[str, Any]
    processing_time: float
    timestamp: datetime
    status: str  # 'processed', 'ignored', 'error'
    error_message: Optional[str] = None

@dataclass
class ErrorRecord:
    """Data class for error records."""
    id: str
    error_type: str
    error_message: str
    timestamp: datetime
    context: Dict[str, Any]
    severity: str  # 'low', 'medium', 'high', 'critical'

class ReportingSystem:
    """Comprehensive reporting and logging system."""
    
    def __init__(self):
        self.db_path = "data/trading_reports.db"
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Statistics tracking
        self.daily_stats = {
            'trades_executed': 0,
            'signals_received': 0,
            'errors_occurred': 0,
            'total_pnl': 0.0,
            'winning_trades': 0,
            'losing_trades': 0
        }
        
        # Group statistics
        self.group_stats = {}
        
    def init_database(self):
        """Initialize SQLite database for storing reports."""
        try:
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    symbol TEXT,
                    side TEXT,
                    quantity REAL,
                    entry_price REAL,
                    exit_price REAL,
                    sl_price REAL,
                    tp_prices TEXT,
                    order_ids TEXT,
                    group_name TEXT,
                    signal_source TEXT,
                    entry_time TEXT,
                    exit_time TEXT,
                    pnl REAL,
                    pnl_percentage REAL,
                    status TEXT,
                    close_reason TEXT,
                    processing_time REAL,
                    admin_command INTEGER
                )
            ''')
            
            # Create signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id TEXT PRIMARY KEY,
                    group_name TEXT,
                    signal_text TEXT,
                    parsed_data TEXT,
                    processing_time REAL,
                    timestamp TEXT,
                    status TEXT,
                    error_message TEXT
                )
            ''')
            
            # Create errors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS errors (
                    id TEXT PRIMARY KEY,
                    error_type TEXT,
                    error_message TEXT,
                    timestamp TEXT,
                    context TEXT,
                    severity TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            log_event("✅ Database initialized successfully", "INFO")
            
        except Exception as e:
            log_event(f"❌ Database initialization failed: {e}", "ERROR")
    
    async def log_trade(self, trade_data: Dict[str, Any]) -> str:
        """Log a trade execution."""
        try:
            trade_id = f"trade_{int(datetime.now().timestamp())}_{trade_data.get('symbol', 'UNKNOWN')}"
            
            trade_record = TradeRecord(
                id=trade_id,
                symbol=trade_data.get('symbol', ''),
                side=trade_data.get('side', ''),
                quantity=trade_data.get('quantity', 0.0),
                entry_price=trade_data.get('entry_price', 0.0),
                exit_price=trade_data.get('exit_price'),
                sl_price=trade_data.get('sl_price'),
                tp_prices=trade_data.get('tp_prices', []),
                order_ids=trade_data.get('order_ids', []),
                group_name=trade_data.get('group_name', ''),
                signal_source=trade_data.get('signal_source', ''),
                entry_time=datetime.now(),
                exit_time=None,
                pnl=None,
                pnl_percentage=None,
                status='open',
                close_reason=None,
                processing_time=trade_data.get('processing_time', 0.0),
                admin_command=trade_data.get('admin_command', False)
            )
            
            # Save to database
            await self.save_trade_record(trade_record)
            
            # Update statistics
            self.daily_stats['trades_executed'] += 1
            
            # Update group statistics
            group_name = trade_record.group_name
            if group_name not in self.group_stats:
                self.group_stats[group_name] = {
                    'trades': 0,
                    'total_pnl': 0.0,
                    'winning_trades': 0,
                    'losing_trades': 0
                }
            self.group_stats[group_name]['trades'] += 1
            
            # Send Telegram notification
            await self.send_trade_notification(trade_record)
            
            log_event(f"✅ Trade logged: {trade_id}", "INFO")
            return trade_id
            
        except Exception as e:
            log_event(f"❌ Failed to log trade: {e}", "ERROR")
            return ""
    
    async def log_signal(self, signal_data: Dict[str, Any]) -> str:
        """Log a signal received."""
        try:
            signal_id = f"signal_{int(datetime.now().timestamp())}_{signal_data.get('group_name', 'UNKNOWN')}"
            
            signal_record = SignalRecord(
                id=signal_id,
                group_name=signal_data.get('group_name', ''),
                signal_text=signal_data.get('signal_text', ''),
                parsed_data=signal_data.get('parsed_data', {}),
                processing_time=signal_data.get('processing_time', 0.0),
                timestamp=datetime.now(),
                status=signal_data.get('status', 'processed'),
                error_message=signal_data.get('error_message')
            )
            
            # Save to database
            await self.save_signal_record(signal_record)
            
            # Update statistics
            self.daily_stats['signals_received'] += 1
            
            # Send Telegram notification for important signals
            if signal_record.status == 'processed':
                await self.send_signal_notification(signal_record)
            
            log_event(f"✅ Signal logged: {signal_id}", "INFO")
            return signal_id
            
        except Exception as e:
            log_event(f"❌ Failed to log signal: {e}", "ERROR")
            return ""
    
    async def log_error(self, error_data: Dict[str, Any]) -> str:
        """Log an error occurrence."""
        try:
            error_id = f"error_{int(datetime.now().timestamp())}_{error_data.get('error_type', 'UNKNOWN')}"
            
            error_record = ErrorRecord(
                id=error_id,
                error_type=error_data.get('error_type', ''),
                error_message=error_data.get('error_message', ''),
                timestamp=datetime.now(),
                context=error_data.get('context', {}),
                severity=error_data.get('severity', 'medium')
            )
            
            # Save to database
            await self.save_error_record(error_record)
            
            # Update statistics
            self.daily_stats['errors_occurred'] += 1
            
            # Send Telegram notification for critical errors
            if error_record.severity in ['high', 'critical']:
                await self.send_error_notification(error_record)
            
            log_event(f"✅ Error logged: {error_id}", "INFO")
            return error_id
            
        except Exception as e:
            log_event(f"❌ Failed to log error: {e}", "ERROR")
            return ""
    
    async def save_trade_record(self, trade_record: TradeRecord):
        """Save trade record to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_record.id,
                trade_record.symbol,
                trade_record.side,
                trade_record.quantity,
                trade_record.entry_price,
                trade_record.exit_price,
                trade_record.sl_price,
                json.dumps(trade_record.tp_prices),
                json.dumps(trade_record.order_ids),
                trade_record.group_name,
                trade_record.signal_source,
                trade_record.entry_time.isoformat(),
                trade_record.exit_time.isoformat() if trade_record.exit_time else None,
                trade_record.pnl,
                trade_record.pnl_percentage,
                trade_record.status,
                trade_record.close_reason,
                trade_record.processing_time,
                1 if trade_record.admin_command else 0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            log_event(f"❌ Failed to save trade record: {e}", "ERROR")
    
    async def save_signal_record(self, signal_record: SignalRecord):
        """Save signal record to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO signals VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_record.id,
                signal_record.group_name,
                signal_record.signal_text,
                json.dumps(signal_record.parsed_data),
                signal_record.processing_time,
                signal_record.timestamp.isoformat(),
                signal_record.status,
                signal_record.error_message
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            log_event(f"❌ Failed to save signal record: {e}", "ERROR")
    
    async def save_error_record(self, error_record: ErrorRecord):
        """Save error record to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO errors VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                error_record.id,
                error_record.error_type,
                error_record.error_message,
                error_record.timestamp.isoformat(),
                json.dumps(error_record.context),
                error_record.severity
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            log_event(f"❌ Failed to save error record: {e}", "ERROR")
    
    async def send_trade_notification(self, trade_record: TradeRecord):
        """Send trade notification to Telegram."""
        try:
            message = f"📈 TRADE EXECUTED\n"
            message += f"Symbol: {trade_record.symbol}\n"
            message += f"Side: {trade_record.side.upper()}\n"
            message += f"Quantity: {trade_record.quantity}\n"
            message += f"Entry Price: ${trade_record.entry_price:,.2f}\n"
            message += f"Group: {trade_record.group_name}\n"
            message += f"Order ID: {trade_record.order_ids[0] if trade_record.order_ids else 'N/A'}\n"
            
            if trade_record.admin_command:
                message += f"🔧 Admin Command\n"
            
            await send_telegram_log(message, tag="trade_execution")
            
        except Exception as e:
            log_event(f"❌ Failed to send trade notification: {e}", "ERROR")
    
    async def send_signal_notification(self, signal_record: SignalRecord):
        """Send signal notification to Telegram."""
        try:
            message = f"📡 SIGNAL PROCESSED\n"
            message += f"Group: {signal_record.group_name}\n"
            message += f"Symbol: {signal_record.parsed_data.get('symbol', 'N/A')}\n"
            message += f"Side: {signal_record.parsed_data.get('side', 'N/A')}\n"
            message += f"Processing Time: {signal_record.processing_time:.3f}s\n"
            
            await send_telegram_log(message, tag="signal_processed")
            
        except Exception as e:
            log_event(f"❌ Failed to send signal notification: {e}", "ERROR")
    
    async def send_error_notification(self, error_record: ErrorRecord):
        """Send error notification to Telegram."""
        try:
            message = f"⚠️ ERROR OCCURRED\n"
            message += f"Type: {error_record.error_type}\n"
            message += f"Severity: {error_record.severity.upper()}\n"
            message += f"Message: {error_record.error_message}\n"
            message += f"Time: {error_record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            await send_telegram_log(message, tag="error_alert")
            
        except Exception as e:
            log_event(f"❌ Failed to send error notification: {e}", "ERROR")
    
    async def generate_daily_report(self, date: datetime = None) -> Dict[str, Any]:
        """Generate daily trading report."""
        try:
            if date is None:
                date = datetime.now()
            
            # Get trades for the day
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            # Get trades
            cursor.execute('''
                SELECT * FROM trades 
                WHERE entry_time >= ? AND entry_time < ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            trades = cursor.fetchall()
            
            # Get signals
            cursor.execute('''
                SELECT * FROM signals 
                WHERE timestamp >= ? AND timestamp < ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            signals = cursor.fetchall()
            
            # Get errors
            cursor.execute('''
                SELECT * FROM errors 
                WHERE timestamp >= ? AND timestamp < ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            errors = cursor.fetchall()
            
            conn.close()
            
            # Calculate statistics
            total_trades = len(trades)
            closed_trades = [t for t in trades if t[15] == 'closed']  # status column
            total_pnl = sum(t[13] or 0 for t in closed_trades)  # pnl column
            winning_trades = len([t for t in closed_trades if (t[13] or 0) > 0])
            losing_trades = len([t for t in closed_trades if (t[13] or 0) < 0])
            
            win_rate = (winning_trades / len(closed_trades) * 100) if closed_trades else 0
            
            # Group statistics
            group_stats = {}
            for trade in trades:
                group_name = trade[9]  # group_name column
                if group_name not in group_stats:
                    group_stats[group_name] = {
                        'trades': 0,
                        'total_pnl': 0.0,
                        'winning_trades': 0,
                        'losing_trades': 0
                    }
                
                group_stats[group_name]['trades'] += 1
                if trade[15] == 'closed' and trade[13]:  # status and pnl
                    pnl = trade[13]
                    group_stats[group_name]['total_pnl'] += pnl
                    if pnl > 0:
                        group_stats[group_name]['winning_trades'] += 1
                    elif pnl < 0:
                        group_stats[group_name]['losing_trades'] += 1
            
            report = {
                'date': date.strftime('%Y-%m-%d'),
                'summary': {
                    'total_trades': total_trades,
                    'closed_trades': len(closed_trades),
                    'total_pnl': total_pnl,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': win_rate,
                    'signals_received': len(signals),
                    'errors_occurred': len(errors)
                },
                'group_stats': group_stats,
                'trades': [self._format_trade_record(t) for t in trades],
                'signals': [self._format_signal_record(s) for s in signals],
                'errors': [self._format_error_record(e) for e in errors]
            }
            
            # Save report to file
            await self.save_report_to_file(report, f"daily_report_{date.strftime('%Y-%m-%d')}.json")
            
            return report
            
        except Exception as e:
            log_event(f"❌ Failed to generate daily report: {e}", "ERROR")
            return {}
    
    async def generate_weekly_report(self, end_date: datetime = None) -> Dict[str, Any]:
        """Generate weekly trading report."""
        try:
            if end_date is None:
                end_date = datetime.now()
            
            start_date = end_date - timedelta(days=7)
            
            # Get all trades for the week
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trades 
                WHERE entry_time >= ? AND entry_time < ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            trades = cursor.fetchall()
            
            # Calculate weekly statistics
            closed_trades = [t for t in trades if t[15] == 'closed']
            total_pnl = sum(t[13] or 0 for t in closed_trades)
            winning_trades = len([t for t in closed_trades if (t[13] or 0) > 0])
            losing_trades = len([t for t in closed_trades if (t[13] or 0) < 0])
            
            win_rate = (winning_trades / len(closed_trades) * 100) if closed_trades else 0
            
            # Daily breakdown
            daily_breakdown = {}
            current_date = start_date
            while current_date < end_date:
                daily_breakdown[current_date.strftime('%Y-%m-%d')] = {
                    'trades': 0,
                    'pnl': 0.0,
                    'winning_trades': 0,
                    'losing_trades': 0
                }
                current_date += timedelta(days=1)
            
            # Fill daily breakdown
            for trade in closed_trades:
                trade_date = datetime.fromisoformat(trade[11]).strftime('%Y-%m-%d')  # entry_time
                if trade_date in daily_breakdown:
                    daily_breakdown[trade_date]['trades'] += 1
                    pnl = trade[13] or 0
                    daily_breakdown[trade_date]['pnl'] += pnl
                    if pnl > 0:
                        daily_breakdown[trade_date]['winning_trades'] += 1
                    elif pnl < 0:
                        daily_breakdown[trade_date]['losing_trades'] += 1
            
            report = {
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                },
                'summary': {
                    'total_trades': len(trades),
                    'closed_trades': len(closed_trades),
                    'total_pnl': total_pnl,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': win_rate,
                    'avg_pnl_per_trade': total_pnl / len(closed_trades) if closed_trades else 0
                },
                'daily_breakdown': daily_breakdown,
                'top_performing_groups': self._get_top_performing_groups(trades),
                'worst_performing_groups': self._get_worst_performing_groups(trades)
            }
            
            # Save report to file
            await self.save_report_to_file(report, f"weekly_report_{end_date.strftime('%Y-%m-%d')}.json")
            
            return report
            
        except Exception as e:
            log_event(f"❌ Failed to generate weekly report: {e}", "ERROR")
            return {}
    
    def _format_trade_record(self, trade_tuple) -> Dict[str, Any]:
        """Format trade record from database tuple."""
        return {
            'id': trade_tuple[0],
            'symbol': trade_tuple[1],
            'side': trade_tuple[2],
            'quantity': trade_tuple[3],
            'entry_price': trade_tuple[4],
            'exit_price': trade_tuple[5],
            'sl_price': trade_tuple[6],
            'tp_prices': json.loads(trade_tuple[7]) if trade_tuple[7] else [],
            'order_ids': json.loads(trade_tuple[8]) if trade_tuple[8] else [],
            'group_name': trade_tuple[9],
            'signal_source': trade_tuple[10],
            'entry_time': trade_tuple[11],
            'exit_time': trade_tuple[12],
            'pnl': trade_tuple[13],
            'pnl_percentage': trade_tuple[14],
            'status': trade_tuple[15],
            'close_reason': trade_tuple[16],
            'processing_time': trade_tuple[17],
            'admin_command': bool(trade_tuple[18])
        }
    
    def _format_signal_record(self, signal_tuple) -> Dict[str, Any]:
        """Format signal record from database tuple."""
        return {
            'id': signal_tuple[0],
            'group_name': signal_tuple[1],
            'signal_text': signal_tuple[2],
            'parsed_data': json.loads(signal_tuple[3]) if signal_tuple[3] else {},
            'processing_time': signal_tuple[4],
            'timestamp': signal_tuple[5],
            'status': signal_tuple[6],
            'error_message': signal_tuple[7]
        }
    
    def _format_error_record(self, error_tuple) -> Dict[str, Any]:
        """Format error record from database tuple."""
        return {
            'id': error_tuple[0],
            'error_type': error_tuple[1],
            'error_message': error_tuple[2],
            'timestamp': error_tuple[3],
            'context': json.loads(error_tuple[4]) if error_tuple[4] else {},
            'severity': error_tuple[5]
        }
    
    def _get_top_performing_groups(self, trades) -> List[Dict[str, Any]]:
        """Get top performing groups by PnL."""
        group_pnl = {}
        for trade in trades:
            if trade[15] == 'closed' and trade[13]:  # status and pnl
                group_name = trade[9]
                pnl = trade[13]
                if group_name not in group_pnl:
                    group_pnl[group_name] = 0.0
                group_pnl[group_name] += pnl
        
        sorted_groups = sorted(group_pnl.items(), key=lambda x: x[1], reverse=True)
        return [{'group': group, 'pnl': pnl} for group, pnl in sorted_groups[:5]]
    
    def _get_worst_performing_groups(self, trades) -> List[Dict[str, Any]]:
        """Get worst performing groups by PnL."""
        group_pnl = {}
        for trade in trades:
            if trade[15] == 'closed' and trade[13]:  # status and pnl
                group_name = trade[9]
                pnl = trade[13]
                if group_name not in group_pnl:
                    group_pnl[group_name] = 0.0
                group_pnl[group_name] += pnl
        
        sorted_groups = sorted(group_pnl.items(), key=lambda x: x[1])
        return [{'group': group, 'pnl': pnl} for group, pnl in sorted_groups[:5]]
    
    async def save_report_to_file(self, report: Dict[str, Any], filename: str):
        """Save report to JSON file."""
        try:
            filepath = self.reports_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            log_event(f"✅ Report saved: {filepath}", "INFO")
            
        except Exception as e:
            log_event(f"❌ Failed to save report: {e}", "ERROR")
    
    async def send_daily_report_to_telegram(self, report: Dict[str, Any]):
        """Send daily report to Telegram."""
        try:
            summary = report.get('summary', {})
            
            message = f"📊 DAILY REPORT - {report.get('date', 'Unknown')}\n"
            message += "=" * 40 + "\n"
            message += f"📈 Total Trades: {summary.get('total_trades', 0)}\n"
            message += f"✅ Closed Trades: {summary.get('closed_trades', 0)}\n"
            message += f"💰 Total PnL: ${summary.get('total_pnl', 0):,.2f}\n"
            message += f"🎯 Win Rate: {summary.get('win_rate', 0):.1f}%\n"
            message += f"📡 Signals: {summary.get('signals_received', 0)}\n"
            message += f"⚠️ Errors: {summary.get('errors_occurred', 0)}\n\n"
            
            # Add group statistics
            group_stats = report.get('group_stats', {})
            if group_stats:
                message += "📋 GROUP PERFORMANCE:\n"
                for group, stats in group_stats.items():
                    if stats['trades'] > 0:
                        win_rate = (stats['winning_trades'] / stats['trades'] * 100) if stats['trades'] > 0 else 0
                        message += f"  {group}: {stats['trades']} trades, ${stats['total_pnl']:,.2f} PnL, {win_rate:.1f}% win rate\n"
            
            await send_telegram_log(message, tag="daily_report")
            
        except Exception as e:
            log_event(f"❌ Failed to send daily report: {e}", "ERROR")
    
    async def send_weekly_report_to_telegram(self, report: Dict[str, Any]):
        """Send weekly report to Telegram."""
        try:
            period = report.get('period', {})
            summary = report.get('summary', {})
            
            message = f"📊 WEEKLY REPORT - {period.get('start_date', 'Unknown')} to {period.get('end_date', 'Unknown')}\n"
            message += "=" * 50 + "\n"
            message += f"📈 Total Trades: {summary.get('total_trades', 0)}\n"
            message += f"✅ Closed Trades: {summary.get('closed_trades', 0)}\n"
            message += f"💰 Total PnL: ${summary.get('total_pnl', 0):,.2f}\n"
            message += f"🎯 Win Rate: {summary.get('win_rate', 0):.1f}%\n"
            message += f"📊 Avg PnL per Trade: ${summary.get('avg_pnl_per_trade', 0):,.2f}\n\n"
            
            # Add top performing groups
            top_groups = report.get('top_performing_groups', [])
            if top_groups:
                message += "🏆 TOP PERFORMING GROUPS:\n"
                for i, group_data in enumerate(top_groups[:3], 1):
                    message += f"  {i}. {group_data['group']}: ${group_data['pnl']:,.2f}\n"
            
            await send_telegram_log(message, tag="weekly_report")
            
        except Exception as e:
            log_event(f"❌ Failed to send weekly report: {e}", "ERROR")

# Global instance
reporting_system = ReportingSystem()

# Test function
async def test_reporting_system():
    """Test the reporting system."""
    print("🧪 TESTING REPORTING SYSTEM")
    print("=" * 40)
    
    # Test logging functions
    print("✅ Testing trade logging...")
    trade_id = await reporting_system.log_trade({
        'symbol': 'BTCUSDT',
        'side': 'buy',
        'quantity': 0.001,
        'entry_price': 67000,
        'sl_price': 65000,
        'tp_prices': [70000],
        'order_ids': ['test_order_1'],
        'group_name': 'Test Group',
        'signal_source': 'manual',
        'processing_time': 0.5,
        'admin_command': True
    })
    print(f"   Trade logged with ID: {trade_id}")
    
    print("✅ Testing signal logging...")
    signal_id = await reporting_system.log_signal({
        'group_name': 'Test Group',
        'signal_text': 'BTCUSDT LONG 67000 65000 70000',
        'parsed_data': {
            'symbol': 'BTCUSDT',
            'side': 'long',
            'entry': 67000,
            'sl': 65000,
            'tp': [70000]
        },
        'processing_time': 0.2,
        'status': 'processed'
    })
    print(f"   Signal logged with ID: {signal_id}")
    
    print("✅ Testing error logging...")
    error_id = await reporting_system.log_error({
        'error_type': 'API_ERROR',
        'error_message': 'Failed to place order',
        'context': {'symbol': 'BTCUSDT', 'action': 'place_order'},
        'severity': 'medium'
    })
    print(f"   Error logged with ID: {error_id}")
    
    # Test report generation
    print("✅ Testing daily report generation...")
    daily_report = await reporting_system.generate_daily_report()
    print(f"   Daily report generated: {len(daily_report.get('trades', []))} trades")
    
    print("✅ Testing weekly report generation...")
    weekly_report = await reporting_system.generate_weekly_report()
    print(f"   Weekly report generated: {len(weekly_report.get('summary', {}))} summary items")
    
    print("✅ Reporting system test completed!")

if __name__ == "__main__":
    asyncio.run(test_reporting_system()) 
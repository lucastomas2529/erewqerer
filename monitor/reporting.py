#!/usr/bin/env python3
"""
Trade reporting and summary module.
Handles generation and sending of trade reports via Telegram.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from config.settings import (
    TELEGRAM_REPORT_ENABLED, 
    REPORT_RECIPIENTS, 
    REPORT_DETAILED_ANALYSIS,
    REPORT_INCLUDE_PYRAMIDING,
    REPORT_INCLUDE_REENTRY,
    REPORT_INCLUDE_CHARTS,
    ENABLE_SIGNAL_ACCURACY_TRACKING
)
from utils.telegram_logger import send_telegram_log
from utils.logger import log_event

# Import accuracy tracking if enabled
if ENABLE_SIGNAL_ACCURACY_TRACKING:
    try:
        from analytics.signal_accuracy import accuracy_tracker
    except ImportError:
        accuracy_tracker = None
else:
    accuracy_tracker = None

@dataclass
class TradeReport:
    """Trade report data structure."""
    symbol: str
    side: str  # "LONG" or "SHORT"
    entry_price: float
    exit_price: float
    quantity: float
    leverage: float
    entry_time: datetime
    exit_time: datetime
    exit_reason: str  # "TP", "SL", "MANUAL", "TIMEOUT"
    pnl_percentage: float
    pnl_usdt: float
    tp_hits: List[float]
    group_name: Optional[str] = None
    pyramiding_steps: List[Dict] = None
    reentry_attempts: int = 0
    break_even_triggered: bool = False
    trailing_activated: bool = False
    final_sl_price: Optional[float] = None

class TradeReporter:
    """Handles trade reporting and summary generation."""
    
    def __init__(self):
        self.trade_history: List[TradeReport] = []
        self.daily_stats: Dict[str, Dict] = {}
    
    async def generate_trade_report(
        self, 
        trade_state, 
        exit_price: float, 
        exit_reason: str,
        group_name: str = None
    ) -> TradeReport:
        """
        Generate a comprehensive trade report from trade state.
        
        Args:
            trade_state: TradeState instance with trade data
            exit_price: Price at which trade was closed
            exit_reason: Reason for exit ("TP", "SL", "MANUAL", "TIMEOUT")
            group_name: Optional group name for context
            
        Returns:
            TradeReport instance with complete trade data
        """
        try:
            # Calculate P&L
            if trade_state.side.upper() == "LONG":
                pnl_percentage = ((exit_price - trade_state.entry_price) / trade_state.entry_price) * 100
            else:
                pnl_percentage = ((trade_state.entry_price - exit_price) / trade_state.entry_price) * 100
            
            # Calculate P&L in USDT
            position_value = trade_state.entry_price * trade_state.quantity
            pnl_usdt = (pnl_percentage / 100) * position_value
            
            # Create trade report
            report = TradeReport(
                symbol=trade_state.symbol,
                side=trade_state.side,
                entry_price=trade_state.entry_price,
                exit_price=exit_price,
                quantity=trade_state.quantity,
                leverage=trade_state.leverage,
                entry_time=datetime.now() - timedelta(hours=1),  # Placeholder - would need actual entry time
                exit_time=datetime.now(),
                exit_reason=exit_reason.upper(),
                pnl_percentage=pnl_percentage,
                pnl_usdt=pnl_usdt,
                tp_hits=trade_state.tp_hits.copy() if trade_state.tp_hits else [],
                group_name=group_name,
                pyramiding_steps=trade_state.pyramid_steps_completed.copy() if trade_state.pyramid_steps_completed else [],
                reentry_attempts=trade_state.reentry_attempts,
                break_even_triggered=trade_state.breakeven_triggered,
                trailing_activated=trade_state.trailing_active,
                final_sl_price=trade_state.sl_price
            )
            
            # Store in history
            self.trade_history.append(report)
            
            # Update daily stats
            await self._update_daily_stats(report)
            
            # Track trade result for accuracy analysis
            if accuracy_tracker and group_name:
                try:
                    # Calculate trade duration in minutes (placeholder)
                    duration_minutes = 60  # Would need actual entry time
                    was_win = pnl_percentage > 0
                    
                    await accuracy_tracker.track_trade_result(
                        group_name=group_name,
                        symbol=trade_state.symbol,
                        side=trade_state.side,
                        entry_price=trade_state.entry_price,
                        exit_price=exit_price,
                        pnl=pnl_usdt,
                        pnl_percent=pnl_percentage,
                        exit_reason=exit_reason.upper(),
                        duration_minutes=duration_minutes,
                        was_win=was_win
                    )
                except Exception as e:
                    log_event(f"[Reporting] Error tracking accuracy: {e}", "ERROR")
            
            return report
            
        except Exception as e:
            log_event(f"[ERROR] Failed to generate trade report for {trade_state.symbol}: {e}", "ERROR")
            return None
    
    async def _update_daily_stats(self, report: TradeReport):
        """Update daily trading statistics."""
        today = report.exit_time.date().isoformat()
        
        if today not in self.daily_stats:
            self.daily_stats[today] = {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "total_pnl_usdt": 0.0,
                "total_pnl_percentage": 0.0,
                "symbols_traded": set(),
                "exit_reasons": {},
                "group_performance": {}
            }
        
        stats = self.daily_stats[today]
        stats["total_trades"] += 1
        stats["total_pnl_usdt"] += report.pnl_usdt
        stats["total_pnl_percentage"] += report.pnl_percentage
        stats["symbols_traded"].add(report.symbol)
        
        if report.pnl_percentage > 0:
            stats["winning_trades"] += 1
        else:
            stats["losing_trades"] += 1
        
        # Track exit reasons
        if report.exit_reason not in stats["exit_reasons"]:
            stats["exit_reasons"][report.exit_reason] = 0
        stats["exit_reasons"][report.exit_reason] += 1
        
        # Track group performance
        if report.group_name:
            if report.group_name not in stats["group_performance"]:
                stats["group_performance"][report.group_name] = {
                    "trades": 0,
                    "pnl_usdt": 0.0,
                    "pnl_percentage": 0.0
                }
            group_stats = stats["group_performance"][report.group_name]
            group_stats["trades"] += 1
            group_stats["pnl_usdt"] += report.pnl_usdt
            group_stats["pnl_percentage"] += report.pnl_percentage
    
    def format_trade_summary(self, report: TradeReport) -> str:
        """
        Format trade report into a readable summary.
        
        Args:
            report: TradeReport instance
            
        Returns:
            Formatted summary string
        """
        try:
            # Calculate trade duration
            duration = report.exit_time - report.entry_time
            duration_str = str(duration).split('.')[0]  # Remove microseconds
            
            # Determine emoji based on P&L
            if report.pnl_percentage > 0:
                pnl_emoji = "🟢"
                pnl_prefix = "+"
            else:
                pnl_emoji = "🔴"
                pnl_prefix = ""
            
            # Determine exit reason emoji
            exit_emojis = {
                "TP": "🎯",
                "SL": "🛑", 
                "MANUAL": "👤",
                "TIMEOUT": "⏰"
            }
            exit_emoji = exit_emojis.get(report.exit_reason, "❓")
            
            # Build summary
            summary = f"""
{pnl_emoji} **TRADE CLOSED** {exit_emoji}

**Symbol:** {report.symbol}
**Side:** {report.side}
**Entry:** ${report.entry_price:,.2f}
**Exit:** ${report.exit_price:,.2f}
**Quantity:** {report.quantity:.4f}
**Leverage:** x{report.leverage}

**P&L:** {pnl_prefix}{report.pnl_percentage:.2f}% ({pnl_prefix}${report.pnl_usdt:.2f})
**Duration:** {duration_str}
**Exit Reason:** {report.exit_reason}
"""
            
            # Add TP hits if any
            if report.tp_hits:
                tp_str = ", ".join([f"TP{i+1}" for i in range(len(report.tp_hits))])
                summary += f"**TP Hits:** {tp_str}\n"
            
            # Add group name if available
            if report.group_name:
                summary += f"**Signal Source:** {report.group_name}\n"
            
            # Add advanced features if enabled and used
            if REPORT_INCLUDE_PYRAMIDING and report.pyramiding_steps:
                summary += f"**Pyramiding Steps:** {len(report.pyramiding_steps)}\n"
            
            if REPORT_INCLUDE_REENTRY and report.reentry_attempts > 0:
                summary += f"**Re-entry Attempts:** {report.reentry_attempts}\n"
            
            if report.break_even_triggered:
                summary += "**Break-Even:** ✅ Triggered\n"
            
            if report.trailing_activated:
                summary += "**Trailing Stop:** ✅ Activated\n"
            
            return summary.strip()
            
        except Exception as e:
            log_event(f"[ERROR] Failed to format trade summary: {e}", "ERROR")
            return f"❌ Error formatting trade summary for {report.symbol}"
    
    def format_detailed_analysis(self, report: TradeReport) -> str:
        """
        Generate detailed trade analysis.
        
        Args:
            report: TradeReport instance
            
        Returns:
            Detailed analysis string
        """
        if not REPORT_DETAILED_ANALYSIS:
            return ""
        
        try:
            analysis = f"""
📊 **DETAILED ANALYSIS**

**Risk Metrics:**
• Risk per Trade: ${report.quantity * report.entry_price * 0.02:.2f} (2% of position)
• Leverage Used: x{report.leverage}
• Position Size: ${report.quantity * report.entry_price:.2f}

**Performance Metrics:**
• ROI: {report.pnl_percentage:.2f}%
• Absolute P&L: ${report.pnl_usdt:.2f}
• Win Rate: {"✅" if report.pnl_percentage > 0 else "❌"}

**Trade Management:**
• Break-Even: {"✅" if report.break_even_triggered else "❌"}
• Trailing Stop: {"✅" if report.trailing_activated else "❌"}
• Final SL: ${report.final_sl_price:.2f} if report.final_sl_price else "N/A"
"""
            
            # Add pyramiding analysis
            if REPORT_INCLUDE_PYRAMIDING and report.pyramiding_steps:
                analysis += f"\n**Pyramiding Analysis:**\n"
                for i, step in enumerate(report.pyramiding_steps, 1):
                    analysis += f"• Step {i}: {step.get('trigger_pol', 0):.2f}% trigger\n"
            
            # Add re-entry analysis
            if REPORT_INCLUDE_REENTRY and report.reentry_attempts > 0:
                analysis += f"\n**Re-entry Analysis:**\n"
                analysis += f"• Attempts: {report.reentry_attempts}\n"
                analysis += f"• Success Rate: {'N/A' if report.reentry_attempts == 0 else '100%' if report.pnl_percentage > 0 else '0%'}\n"
            
            return analysis.strip()
            
        except Exception as e:
            log_event(f"[ERROR] Failed to generate detailed analysis: {e}", "ERROR")
            return ""
    
    async def send_trade_report(self, report: TradeReport, group_name: str = None):
        """
        Send trade report via Telegram.
        
        Args:
            report: TradeReport instance
            group_name: Optional group name for context
        """
        if not TELEGRAM_REPORT_ENABLED:
            return
        
        try:
            # Format the report
            summary = self.format_trade_summary(report)
            detailed_analysis = self.format_detailed_analysis(report)
            
            # Combine summary and analysis
            full_report = summary
            if detailed_analysis:
                full_report += "\n\n" + detailed_analysis
            
            # Send to all recipients
            for recipient in REPORT_RECIPIENTS:
                try:
                    await send_telegram_log(
                        full_report, 
                        group_name=group_name or recipient,
                        tag="trade_report"
                    )
                    log_event(f"[REPORT] Trade report sent to {recipient}", "INFO")
                except Exception as e:
                    log_event(f"[ERROR] Failed to send report to {recipient}: {e}", "ERROR")
            
            # Also send to the original group if different from recipients
            if group_name and group_name not in REPORT_RECIPIENTS:
                try:
                    await send_telegram_log(
                        summary,  # Send only summary to original group
                        group_name=group_name,
                        tag="trade_report"
                    )
                except Exception as e:
                    log_event(f"[ERROR] Failed to send report to original group {group_name}: {e}", "ERROR")
                    
        except Exception as e:
            log_event(f"[ERROR] Failed to send trade report: {e}", "ERROR")
    
    async def generate_trade_chart(self, trade_state, exit_price: float) -> Optional[str]:
        """
        Generate a chart for the completed trade.
        
        Args:
            trade_state: TradeState instance with trade data
            exit_price: Price at which trade was closed
            
        Returns:
            Local image path or Telegram upload URL, or None if chart generation fails
        """
        if not REPORT_INCLUDE_CHARTS:
            return None
        
        try:
            import os
            import random
            from datetime import datetime, timedelta
            
            # Create charts directory if it doesn't exist
            charts_dir = "data/charts"
            os.makedirs(charts_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_suffix = random.randint(1000, 9999)
            filename = f"{trade_state.symbol}_{timestamp}_{random_suffix}.{CHART_IMAGE_FORMAT}"
            filepath = os.path.join(charts_dir, filename)
            
            # Generate mock chart data (in real implementation, this would fetch from exchange)
            chart_data = self._generate_mock_chart_data(trade_state, exit_price)
            
            # Create chart using matplotlib
            chart_url = await self._create_chart_image(chart_data, filepath, trade_state, exit_price)
            
            if chart_url:
                log_event(f"📊 Chart generated successfully: {filepath}", "INFO")
                return chart_url
            else:
                log_event(f"⚠️ Chart generation failed for {trade_state.symbol}", "WARNING")
                return None
                
        except Exception as e:
            log_event(f"❌ Error generating chart for {trade_state.symbol}: {e}", "ERROR")
            return None
    
    def _generate_mock_chart_data(self, trade_state, exit_price: float) -> Dict:
        """Generate mock chart data for demonstration purposes."""
        import random
        from datetime import datetime, timedelta
        
        # Generate mock OHLCV data
        data = {
            'timestamps': [],
            'open': [],
            'high': [],
            'low': [],
            'close': [],
            'volume': []
        }
        
        # Generate data points around the trade
        base_price = trade_state.entry_price
        current_time = datetime.now() - timedelta(hours=CHART_LOOKBACK_PERIODS)
        
        for i in range(CHART_LOOKBACK_PERIODS):
            # Add some randomness to price movement
            price_change = random.uniform(-0.02, 0.02)  # ±2% change
            base_price *= (1 + price_change)
            
            # Generate OHLC for this candle
            open_price = base_price
            high_price = open_price * random.uniform(1.0, 1.01)
            low_price = open_price * random.uniform(0.99, 1.0)
            close_price = random.uniform(low_price, high_price)
            volume = random.uniform(1000, 10000)
            
            data['timestamps'].append(current_time)
            data['open'].append(open_price)
            data['high'].append(high_price)
            data['low'].append(low_price)
            data['close'].append(close_price)
            data['volume'].append(volume)
            
            current_time += timedelta(hours=1)
        
        return data
    
    async def _create_chart_image(self, chart_data: Dict, filepath: str, trade_state, exit_price: float) -> Optional[str]:
        """Create chart image using matplotlib."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from matplotlib.patches import Rectangle
            import numpy as np
            
            # Set theme
            if CHART_THEME == "dark":
                plt.style.use('dark_background')
            else:
                plt.style.use('default')
            
            # Create figure and subplots
            if CHART_SHOW_VOLUME:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))
            
            # Convert timestamps to matplotlib dates
            dates = mdates.date2num(chart_data['timestamps'])
            
            # Plot candlestick chart
            self._plot_candlesticks(ax1, dates, chart_data, trade_state, exit_price)
            
            # Plot volume if enabled
            if CHART_SHOW_VOLUME and 'ax2' in locals():
                self._plot_volume(ax2, dates, chart_data)
            
            # Add technical indicators if enabled
            if CHART_SHOW_INDICATORS:
                self._add_technical_indicators(ax1, dates, chart_data)
            
            # Customize chart
            ax1.set_title(f'{trade_state.symbol} Trade Chart - {trade_state.side} @ ${trade_state.entry_price:.2f}', 
                         fontsize=14, fontweight='bold')
            ax1.set_ylabel('Price (USDT)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # Format x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax1.xaxis.set_major_locator(mdates.HourLocator(interval=6))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # Add trade annotations
            self._add_trade_annotations(ax1, trade_state, exit_price, dates)
            
            # Save chart
            plt.tight_layout()
            plt.savefig(filepath, dpi=300, bbox_inches='tight', 
                       format=CHART_IMAGE_FORMAT, quality=CHART_IMAGE_QUALITY)
            plt.close()
            
            # Upload to Telegram if enabled
            if CHART_UPLOAD_TO_TELEGRAM:
                try:
                    chart_url = await self._upload_chart_to_telegram(filepath)
                    return chart_url
                except Exception as e:
                    log_event(f"⚠️ Failed to upload chart to Telegram: {e}", "WARNING")
                    return filepath if CHART_SAVE_LOCALLY else None
            
            return filepath if CHART_SAVE_LOCALLY else None
            
        except Exception as e:
            log_event(f"❌ Error creating chart image: {e}", "ERROR")
            return None
    
    def _plot_candlesticks(self, ax, dates, chart_data, trade_state, exit_price):
        """Plot candlestick chart with trade markers."""
        import matplotlib.patches as patches
        
        # Plot candlesticks
        for i in range(len(dates)):
            open_price = chart_data['open'][i]
            close_price = chart_data['close'][i]
            high_price = chart_data['high'][i]
            low_price = chart_data['low'][i]
            
            # Determine color based on open/close
            color = 'green' if close_price >= open_price else 'red'
            
            # Plot body
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)
            
            rect = patches.Rectangle((dates[i] - 0.02, body_bottom), 0.04, body_height,
                                   facecolor=color, edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            
            # Plot wicks
            ax.plot([dates[i], dates[i]], [low_price, high_price], color='black', linewidth=1)
    
    def _plot_volume(self, ax, dates, chart_data):
        """Plot volume bars."""
        colors = ['green' if close >= open else 'red' 
                 for open, close in zip(chart_data['open'], chart_data['close'])]
        
        ax.bar(dates, chart_data['volume'], color=colors, alpha=0.7, width=0.04)
        ax.set_ylabel('Volume', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _add_technical_indicators(self, ax, dates, chart_data):
        """Add technical indicators to the chart."""
        import numpy as np
        
        # Simple Moving Averages
        closes = np.array(chart_data['close'])
        
        # 20-period SMA
        if len(closes) >= 20:
            sma_20 = np.convolve(closes, np.ones(20)/20, mode='valid')
            sma_dates = dates[19:]  # Adjust dates for SMA
            ax.plot(sma_dates, sma_20, color='blue', linewidth=2, label='SMA 20')
        
        # 50-period SMA
        if len(closes) >= 50:
            sma_50 = np.convolve(closes, np.ones(50)/50, mode='valid')
            sma_dates = dates[49:]  # Adjust dates for SMA
            ax.plot(sma_dates, sma_50, color='orange', linewidth=2, label='SMA 50')
        
        ax.legend()
    
    def _add_trade_annotations(self, ax, trade_state, exit_price, dates):
        """Add trade entry/exit annotations to the chart."""
        import matplotlib.patches as patches
        
        # Entry point
        entry_idx = len(dates) // 2  # Place entry in middle of chart
        ax.scatter(dates[entry_idx], trade_state.entry_price, 
                  color='blue', s=100, marker='^', zorder=5, label='Entry')
        ax.annotate(f'Entry\n${trade_state.entry_price:.2f}', 
                   xy=(dates[entry_idx], trade_state.entry_price),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='blue', alpha=0.7),
                   fontsize=10, color='white')
        
        # Exit point
        exit_idx = len(dates) - 1
        ax.scatter(dates[exit_idx], exit_price, 
                  color='red', s=100, marker='v', zorder=5, label='Exit')
        ax.annotate(f'Exit\n${exit_price:.2f}', 
                   xy=(dates[exit_idx], exit_price),
                   xytext=(10, -20), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.7),
                   fontsize=10, color='white')
        
        # Stop Loss line
        if trade_state.stop_loss:
            ax.axhline(y=trade_state.stop_loss, color='red', linestyle='--', 
                      alpha=0.7, label=f'SL: ${trade_state.stop_loss:.2f}')
        
        # Take Profit levels
        if trade_state.take_profit:
            for i, tp in enumerate(trade_state.take_profit[:4]):  # Show first 4 TP levels
                ax.axhline(y=tp, color='green', linestyle='--', alpha=0.7,
                          label=f'TP{i+1}: ${tp:.2f}')
        
        ax.legend(loc='upper left')
    
    async def _upload_chart_to_telegram(self, filepath: str) -> Optional[str]:
        """Upload chart image to Telegram and return URL."""
        try:
            # This would integrate with Telegram Bot API to upload image
            # For now, return a mock URL
            filename = os.path.basename(filepath)
            mock_url = f"https://t.me/charts/{filename}"
            
            log_event(f"📤 Chart uploaded to Telegram: {mock_url}", "INFO")
            return mock_url
            
        except Exception as e:
            log_event(f"❌ Error uploading chart to Telegram: {e}", "ERROR")
            return None

    def get_daily_summary(self, date: str = None) -> str:
        """
        Generate daily trading summary.
        
        Args:
            date: Date string (YYYY-MM-DD) or None for today
            
        Returns:
            Daily summary string
        """
        if date is None:
            date = datetime.now().date().isoformat()
        
        if date not in self.daily_stats:
            return f"📊 No trading activity on {date}"
        
        stats = self.daily_stats[date]
        
        # Calculate win rate
        win_rate = (stats["winning_trades"] / stats["total_trades"] * 100) if stats["total_trades"] > 0 else 0
        
        # Determine overall performance emoji
        if stats["total_pnl_percentage"] > 0:
            performance_emoji = "🟢"
            pnl_prefix = "+"
        else:
            performance_emoji = "🔴"
            pnl_prefix = ""
        
        summary = f"""
{performance_emoji} **DAILY TRADING SUMMARY** - {date}

**Overview:**
• Total Trades: {stats['total_trades']}
• Winning Trades: {stats['winning_trades']}
• Losing Trades: {stats['losing_trades']}
• Win Rate: {win_rate:.1f}%

**Performance:**
• Total P&L: {pnl_prefix}{stats['total_pnl_percentage']:.2f}%
• Total P&L (USDT): {pnl_prefix}${stats['total_pnl_usdt']:.2f}

**Symbols Traded:** {', '.join(sorted(stats['symbols_traded']))}

**Exit Reasons:**
"""
        
        for reason, count in stats["exit_reasons"].items():
            summary += f"• {reason}: {count}\n"
        
        # Add group performance if available
        if stats["group_performance"]:
            summary += "\n**Group Performance:**\n"
            for group, perf in stats["group_performance"].items():
                group_win_rate = (perf["pnl_percentage"] / perf["trades"]) if perf["trades"] > 0 else 0
                summary += f"• {group}: {perf['trades']} trades, {group_win_rate:.2f}% avg\n"
        
        # Add signal accuracy if available
        if accuracy_tracker:
            try:
                accuracy_report = accuracy_tracker.generate_accuracy_report("1d")
                if "No trading activity" not in accuracy_report:
                    summary += f"\n{accuracy_report}"
            except Exception as e:
                log_event(f"[Reporting] Error generating accuracy report: {e}", "ERROR")
        
        return summary.strip()

# Global reporter instance
trade_reporter = TradeReporter()

async def generate_trade_report(
    trade_state, 
    exit_price: float, 
    exit_reason: str,
    group_name: str = None
) -> Optional[TradeReport]:
    """
    Convenience function to generate and send trade report.
    
    Args:
        trade_state: TradeState instance
        exit_price: Exit price
        exit_reason: Exit reason
        group_name: Optional group name
        
    Returns:
        TradeReport instance or None if failed
    """
    try:
        # Generate report
        report = await trade_reporter.generate_trade_report(
            trade_state, exit_price, exit_reason, group_name
        )
        
        if report:
            # Send report
            await trade_reporter.send_trade_report(report, group_name)
            log_event(f"[REPORT] Trade report generated for {trade_state.symbol}", "INFO")
        
        return report
        
    except Exception as e:
        log_event(f"[ERROR] Failed to generate trade report: {e}", "ERROR")
        return None 
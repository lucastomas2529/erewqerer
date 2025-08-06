# Real-time Telegram Group Monitoring System
"""
Monitor the health, performance, and signal quality of multiple Telegram groups in real-time.
Provides dashboards, alerts, and performance metrics for multi-group signal processing.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque

from config.settings import TelegramConfig
from utils.telegram_logger import send_telegram_log

@dataclass
class GroupMetrics:
    """Metrics for a single Telegram group."""
    name: str
    group_id: int
    
    # Signal statistics
    total_signals: int = 0
    valid_signals: int = 0
    invalid_signals: int = 0
    signals_last_hour: int = 0
    signals_last_day: int = 0
    
    # Quality metrics
    avg_confidence: float = 0.0
    high_confidence_signals: int = 0  # confidence > 0.8
    medium_confidence_signals: int = 0  # 0.5 < confidence <= 0.8
    low_confidence_signals: int = 0  # confidence <= 0.5
    
    # Timing metrics
    last_signal_time: Optional[datetime] = None
    avg_time_between_signals: float = 0.0
    longest_silence: float = 0.0  # hours
    
    # Error tracking
    parse_errors: int = 0
    connection_errors: int = 0
    spam_filtered: int = 0
    
    # Performance tracking
    processing_times: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_signals: deque = field(default_factory=lambda: deque(maxlen=50))
    
    def update_signal_metrics(self, signal_data: Dict, processing_time: float):
        """Update metrics when a new signal is processed."""
        now = datetime.now()
        
        # Basic counts
        self.total_signals += 1
        if signal_data:
            self.valid_signals += 1
            confidence = signal_data.get("confidence", 0.0)
            
            # Confidence tracking
            if confidence > 0.8:
                self.high_confidence_signals += 1
            elif confidence > 0.5:
                self.medium_confidence_signals += 1
            else:
                self.low_confidence_signals += 1
            
            # Update average confidence
            total_confident = self.high_confidence_signals + self.medium_confidence_signals + self.low_confidence_signals
            if total_confident > 0:
                self.avg_confidence = (
                    (self.high_confidence_signals * 0.9) +
                    (self.medium_confidence_signals * 0.65) +
                    (self.low_confidence_signals * 0.25)
                ) / total_confident
            
            # Recent signals tracking
            self.recent_signals.append({
                "timestamp": now,
                "symbol": signal_data.get("symbol", "Unknown"),
                "side": signal_data.get("side", "Unknown"),
                "confidence": confidence,
                "has_sl": signal_data.get("has_sl", False),
                "has_targets": signal_data.get("has_targets", False)
            })
            
        else:
            self.invalid_signals += 1
        
        # Timing updates
        if self.last_signal_time:
            time_diff = (now - self.last_signal_time).total_seconds() / 3600  # hours
            
            # Update average time between signals
            if self.total_signals > 1:
                self.avg_time_between_signals = (
                    (self.avg_time_between_signals * (self.total_signals - 2)) + time_diff
                ) / (self.total_signals - 1)
            
            # Track longest silence
            if time_diff > self.longest_silence:
                self.longest_silence = time_diff
        
        self.last_signal_time = now
        
        # Performance tracking
        self.processing_times.append(processing_time)
        
        # Time-based counts
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        self.signals_last_hour = sum(
            1 for s in self.recent_signals 
            if s["timestamp"] > one_hour_ago
        )
        
        self.signals_last_day = sum(
            1 for s in self.recent_signals 
            if s["timestamp"] > one_day_ago
        )
    
    def get_health_score(self) -> float:
        """Calculate overall health score (0.0 to 1.0)."""
        if self.total_signals == 0:
            return 0.0
        
        # Valid signal ratio (40% weight)
        valid_ratio = self.valid_signals / self.total_signals
        
        # Confidence score (30% weight)
        confidence_score = self.avg_confidence
        
        # Activity score (20% weight) - based on recent activity
        activity_score = min(1.0, self.signals_last_hour / 10.0)  # 10 signals/hour = 100%
        
        # Error rate (10% weight)
        error_rate = (self.parse_errors + self.connection_errors) / max(1, self.total_signals)
        error_score = max(0.0, 1.0 - error_rate)
        
        health_score = (
            valid_ratio * 0.4 +
            confidence_score * 0.3 +
            activity_score * 0.2 +
            error_score * 0.1
        )
        
        return min(1.0, max(0.0, health_score))

class GroupMonitor:
    """Real-time monitoring system for multiple Telegram groups."""
    
    def __init__(self):
        self.group_metrics: Dict[str, GroupMetrics] = {}
        self.monitoring_active = False
        self.alert_thresholds = {
            "min_health_score": 0.6,
            "max_silence_hours": 6.0,
            "min_signals_per_hour": 1,
            "min_confidence": 0.4
        }
        
        # Initialize metrics for all configured groups
        self._initialize_group_metrics()
        
    def _initialize_group_metrics(self):
        """Initialize metrics for all configured Telegram groups."""
        for group_name, group_id in TelegramConfig.TELEGRAM_GROUPS.items():
            self.group_metrics[group_name] = GroupMetrics(
                name=group_name,
                group_id=group_id
            )
        
        print(f"📊 Initialized monitoring for {len(self.group_metrics)} groups")
    
    async def record_signal(self, group_name: str, signal_data: Dict, processing_time: float):
        """Record a new signal for monitoring."""
        if group_name not in self.group_metrics:
            # Create new metrics for unknown group
            self.group_metrics[group_name] = GroupMetrics(
                name=group_name,
                group_id=0  # Unknown ID
            )
        
        metrics = self.group_metrics[group_name]
        metrics.update_signal_metrics(signal_data, processing_time)
        
        # Check for alerts
        await self._check_alerts(group_name, metrics)
    
    async def record_error(self, group_name: str, error_type: str):
        """Record an error for a specific group."""
        if group_name in self.group_metrics:
            metrics = self.group_metrics[group_name]
            if error_type == "parse":
                metrics.parse_errors += 1
            elif error_type == "connection":
                metrics.connection_errors += 1
            elif error_type == "spam":
                metrics.spam_filtered += 1
    
    async def _check_alerts(self, group_name: str, metrics: GroupMetrics):
        """Check if any alerts should be triggered for a group."""
        alerts = []
        
        # Health score alert
        health_score = metrics.get_health_score()
        if health_score < self.alert_thresholds["min_health_score"]:
            alerts.append(f"🔴 Low health score: {health_score:.2f}")
        
        # Silence alert
        if metrics.last_signal_time:
            hours_since_last = (datetime.now() - metrics.last_signal_time).total_seconds() / 3600
            if hours_since_last > self.alert_thresholds["max_silence_hours"]:
                alerts.append(f"⏰ Silent for {hours_since_last:.1f} hours")
        
        # Activity alert
        if metrics.signals_last_hour < self.alert_thresholds["min_signals_per_hour"]:
            alerts.append(f"📉 Low activity: {metrics.signals_last_hour} signals/hour")
        
        # Confidence alert
        if metrics.avg_confidence < self.alert_thresholds["min_confidence"]:
            alerts.append(f"⚠️ Low signal quality: {metrics.avg_confidence:.2f} avg confidence")
        
        # Send alerts if any
        if alerts:
            alert_message = f"🚨 Alerts for {group_name}:\n" + "\n".join(alerts)
            await send_telegram_log(alert_message, tag="group_alert")
    
    def get_group_status(self, group_name: str) -> Dict[str, Any]:
        """Get detailed status for a specific group."""
        if group_name not in self.group_metrics:
            return {"error": "Group not found"}
        
        metrics = self.group_metrics[group_name]
        
        return {
            "name": group_name,
            "group_id": metrics.group_id,
            "health_score": metrics.get_health_score(),
            "total_signals": metrics.total_signals,
            "valid_signals": metrics.valid_signals,
            "success_rate": metrics.valid_signals / max(1, metrics.total_signals) * 100,
            "avg_confidence": metrics.avg_confidence,
            "signals_last_hour": metrics.signals_last_hour,
            "signals_last_day": metrics.signals_last_day,
            "last_signal": metrics.last_signal_time.isoformat() if metrics.last_signal_time else None,
            "avg_processing_time": sum(metrics.processing_times) / len(metrics.processing_times) if metrics.processing_times else 0,
            "errors": {
                "parse": metrics.parse_errors,
                "connection": metrics.connection_errors,
                "spam": metrics.spam_filtered
            }
        }
    
    def get_overall_dashboard(self) -> Dict[str, Any]:
        """Get overall monitoring dashboard."""
        total_groups = len(self.group_metrics)
        active_groups = sum(1 for m in self.group_metrics.values() if m.total_signals > 0)
        
        # Calculate aggregate metrics
        total_signals = sum(m.total_signals for m in self.group_metrics.values())
        total_valid = sum(m.valid_signals for m in self.group_metrics.values())
        avg_health = sum(m.get_health_score() for m in self.group_metrics.values()) / max(1, total_groups)
        
        # Top performing groups
        top_groups = sorted(
            self.group_metrics.items(),
            key=lambda x: x[1].get_health_score(),
            reverse=True
        )[:5]
        
        # Groups needing attention
        problem_groups = [
            name for name, metrics in self.group_metrics.items()
            if metrics.get_health_score() < 0.6
        ]
        
        return {
            "overview": {
                "total_groups": total_groups,
                "active_groups": active_groups,
                "total_signals_processed": total_signals,
                "overall_success_rate": total_valid / max(1, total_signals) * 100,
                "average_health_score": avg_health
            },
            "top_performing_groups": [
                {"name": name, "health_score": metrics.get_health_score()}
                for name, metrics in top_groups
            ],
            "groups_needing_attention": problem_groups,
            "timestamp": datetime.now().isoformat()
        }
    
    async def start_monitoring(self):
        """Start the monitoring system."""
        self.monitoring_active = True
        print("🎯 Group monitoring system started")
        
        # Start periodic status reports
        asyncio.create_task(self._periodic_status_reports())
    
    async def stop_monitoring(self):
        """Stop the monitoring system."""
        self.monitoring_active = False
        print("🛑 Group monitoring system stopped")
    
    async def _periodic_status_reports(self):
        """Send periodic status reports."""
        while self.monitoring_active:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                dashboard = self.get_overall_dashboard()
                
                status_message = f"""
📊 **Hourly Group Monitoring Report**

📈 **Overview:**
• Active Groups: {dashboard['overview']['active_groups']}/{dashboard['overview']['total_groups']}
• Signals Processed: {dashboard['overview']['total_signals_processed']}
• Success Rate: {dashboard['overview']['overall_success_rate']:.1f}%
• Avg Health Score: {dashboard['overview']['average_health_score']:.2f}

🏆 **Top Groups:**
{chr(10).join(f"• {g['name']}: {g['health_score']:.2f}" for g in dashboard['top_performing_groups'][:3])}

⚠️ **Attention Needed:** {len(dashboard['groups_needing_attention'])} groups
                """.strip()
                
                await send_telegram_log(status_message, tag="monitoring_report")
                
            except Exception as e:
                print(f"❌ Error in periodic monitoring: {e}")

# Global monitor instance
group_monitor = GroupMonitor()

# Convenience functions
async def record_signal_processing(group_name: str, signal_data: Dict, processing_time: float):
    """Record signal processing for monitoring."""
    await group_monitor.record_signal(group_name, signal_data, processing_time)

async def record_group_error(group_name: str, error_type: str):
    """Record an error for monitoring."""
    await group_monitor.record_error(group_name, error_type)

def get_monitoring_dashboard():
    """Get the current monitoring dashboard."""
    return group_monitor.get_overall_dashboard()

async def start_group_monitoring():
    """Start the group monitoring system."""
    await group_monitor.start_monitoring()

if __name__ == "__main__":
    print("📊 Group Monitor Test")
    print("=" * 40)
    
    async def test_monitoring():
        # Test the monitoring system
        await group_monitor.start_monitoring()
        
        # Simulate some signals
        test_signal = {
            "symbol": "BTCUSDT",
            "side": "LONG",
            "confidence": 0.85,
            "has_sl": True,
            "has_targets": True
        }
        
        await group_monitor.record_signal("test_group", test_signal, 0.05)
        await group_monitor.record_signal("test_group", None, 0.03)  # Failed signal
        
        # Get status
        status = group_monitor.get_group_status("test_group")
        print(f"Test group status: {status}")
        
        dashboard = group_monitor.get_overall_dashboard()
        print(f"Dashboard: {dashboard}")
        
        await group_monitor.stop_monitoring()
    
    asyncio.run(test_monitoring())
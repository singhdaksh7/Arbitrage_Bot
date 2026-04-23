"""
Alert system for high-profit opportunities
"""

from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AlertType(Enum):
    """Alert types"""
    HIGH_PROFIT = "high_profit"
    PRICE_SPIKE = "price_spike"
    TRADE_EXECUTED = "trade_executed"
    PROFIT_MILESTONE = "profit_milestone"

class Alert:
    """Represents an alert"""
    
    def __init__(self, alert_type, message, data=None):
        self.type = alert_type
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.utcnow()
        self.read = False
    
    def to_dict(self):
        return {
            'type': self.type.value,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'read': self.read
        }

class AlertManager:
    """Manages alerts"""
    
    def __init__(self):
        self.alerts = []
        self.max_alerts = 100
    
    def add_alert(self, alert_type, message, data=None):
        """Add new alert"""
        alert = Alert(alert_type, message, data)
        self.alerts.insert(0, alert)  # Most recent first
        
        # Keep only last 100 alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[:self.max_alerts]
        
        logger.info(f"🔔 Alert: {message}")
        return alert
    
    def get_alerts(self, limit=20):
        """Get recent alerts"""
        return [a.to_dict() for a in self.alerts[:limit]]
    
    def mark_as_read(self, index):
        """Mark alert as read"""
        if 0 <= index < len(self.alerts):
            self.alerts[index].read = True
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []

# Global alert manager
alert_manager = AlertManager()

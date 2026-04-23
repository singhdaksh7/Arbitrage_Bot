"""
Arbitrage opportunity model
"""

from app import db
from datetime import datetime

class Opportunity(db.Model):
    """Detected arbitrage opportunity"""
    __tablename__ = 'opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Trading pair
    trading_pair = db.Column(db.String(20), nullable=False)  # e.g., 'BTC/USD'
    
    # Exchange details
    buy_exchange = db.Column(db.String(20), nullable=False)
    sell_exchange = db.Column(db.String(20), nullable=False)
    
    # Prices
    buy_price = db.Column(db.Float, nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    
    # Profitability
    price_difference = db.Column(db.Float, nullable=False)
    price_difference_percent = db.Column(db.Float, nullable=False)
    profit_after_fees = db.Column(db.Float, nullable=False)
    profit_percent = db.Column(db.Float, nullable=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_executed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Opportunity {self.trading_pair} {self.profit_percent:.2f}%>'
    
    def to_dict(self):
        """Convert opportunity to dictionary"""
        return {
            'id': self.id,
            'trading_pair': self.trading_pair,
            'buy_exchange': self.buy_exchange,
            'sell_exchange': self.sell_exchange,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'price_difference': self.price_difference,
            'price_difference_percent': self.price_difference_percent,
            'profit_after_fees': self.profit_after_fees,
            'profit_percent': self.profit_percent,
            'is_active': self.is_active,
            'is_executed': self.is_executed,
            'detected_at': self.detected_at.isoformat()
        }

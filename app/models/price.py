"""
Price snapshot model for historical tracking
"""

from app import db
from datetime import datetime

class PriceSnapshot(db.Model):
    """Historical price snapshot from exchanges"""
    __tablename__ = 'price_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    
    trading_pair = db.Column(db.String(20), nullable=False)
    exchange = db.Column(db.String(20), nullable=False)
    
    bid_price = db.Column(db.Float)
    ask_price = db.Column(db.Float)
    last_price = db.Column(db.Float)
    
    volume_24h = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_pair_exchange_timestamp', 'trading_pair', 'exchange', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<PriceSnapshot {self.trading_pair} {self.exchange} {self.last_price}>'

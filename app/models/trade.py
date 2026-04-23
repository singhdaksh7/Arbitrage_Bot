"""
Trade model for tracking simulated transactions
"""

from app import db
from datetime import datetime

class Trade(db.Model):
    """Simulated trade record"""
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    
    # Trade details
    trading_pair = db.Column(db.String(20), nullable=False)  # e.g., 'BTC/USD'
    trade_type = db.Column(db.String(10), nullable=False)    # 'BUY' or 'SELL'
    exchange = db.Column(db.String(20), nullable=False)      # 'binance', 'kraken', etc.
    
    # Amounts
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    net_cost = db.Column(db.Float, nullable=False)  # total_cost + fee (for buy) or total_cost - fee (for sell)
    
    # Status
    status = db.Column(db.String(20), default='completed')   # 'pending', 'completed', 'failed'
    profit_loss = db.Column(db.Float, default=0)
    profit_loss_percent = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    opportunity = db.relationship('Opportunity', backref='trades')
    
    def __repr__(self):
        return f'<Trade {self.trade_type} {self.quantity} {self.trading_pair} @ {self.price}>'
    
    def to_dict(self):
        """Convert trade to dictionary"""
        return {
            'id': self.id,
            'trading_pair': self.trading_pair,
            'type': self.trade_type,
            'exchange': self.exchange,
            'quantity': self.quantity,
            'price': self.price,
            'total_cost': self.total_cost,
            'fee': self.fee,
            'net_cost': self.net_cost,
            'status': self.status,
            'profit_loss': self.profit_loss,
            'profit_loss_percent': self.profit_loss_percent,
            'created_at': self.created_at.isoformat()
        }

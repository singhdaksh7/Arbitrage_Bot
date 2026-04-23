"""
Virtual wallet model for paper trading
"""

from app import db
from datetime import datetime

class Wallet(db.Model):
    """User's virtual wallet for paper trading"""
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    usd_balance = db.Column(db.Float, default=0)
    total_invested = db.Column(db.Float, default=0)
    total_profit_loss = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holdings = db.relationship('Holding', backref='wallet', lazy=True, cascade='all, delete-orphan')
    trades = db.relationship('Trade', backref='wallet', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Wallet USD: ${self.usd_balance:.2f}>'
    
    def get_total_value(self):
        """Calculate total portfolio value"""
        holdings_value = sum(h.get_current_value() for h in self.holdings)
        return self.usd_balance + holdings_value
    
    def can_afford(self, amount):
        """Check if wallet has enough USD"""
        return self.usd_balance >= amount
    
    def add_funds(self, amount):
        """Add USD to wallet"""
        self.usd_balance += amount
        self.updated_at = datetime.utcnow()
        return self.usd_balance
    
    def withdraw_funds(self, amount):
        """Withdraw USD from wallet"""
        if self.can_afford(amount):
            self.usd_balance -= amount
            self.updated_at = datetime.utcnow()
            return True
        return False


class Holding(db.Model):
    """Cryptocurrency holdings in wallet"""
    __tablename__ = 'holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)  # e.g., 'BTC', 'ETH'
    quantity = db.Column(db.Float, nullable=False)
    avg_buy_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Holding {self.symbol}: {self.quantity}>'
    
    def get_current_value(self):
        """Calculate current value of holding"""
        return self.quantity * self.current_price
    
    def get_unrealized_pnl(self):
        """Calculate unrealized profit/loss"""
        return (self.current_price - self.avg_buy_price) * self.quantity
    
    def get_unrealized_pnl_percent(self):
        """Calculate unrealized profit/loss percentage"""
        if self.avg_buy_price == 0:
            return 0
        return ((self.current_price - self.avg_buy_price) / self.avg_buy_price) * 100

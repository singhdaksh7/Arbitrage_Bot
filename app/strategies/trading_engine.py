"""
Paper trading engine
"""

from app import db
from app.models.wallet import Wallet, Holding
from app.models.trade import Trade
from config import Config
from datetime import datetime

class TradingEngine:
    """Simulates trades on detected opportunities"""
    
    def __init__(self):
        self.fee = Config.TRANSACTION_FEE
    
    def get_or_create_wallet(self, initial_balance=None):
        """Get existing wallet or create new one"""
        wallet = Wallet.query.first()
        
        if not wallet:
            balance = initial_balance or Config.INITIAL_WALLET_BALANCE
            wallet = Wallet(usd_balance=balance)
            db.session.add(wallet)
            db.session.commit()
            print(f"💰 Created new wallet with ${balance:.2f}")
        
        return wallet
    
    def execute_trade(self, opportunity, quantity=None):
        """
        Execute a simulated arbitrage trade
        
        Args:
            opportunity: Opportunity object
            quantity: Amount of crypto to buy (if None, calculate from wallet)
        
        Returns: Trade object or None if failed
        """
        wallet = self.get_or_create_wallet()
        
        if not wallet.can_afford(opportunity.buy_price):
            print(f"❌ Insufficient funds for {opportunity.trading_pair}")
            return None
        
        # Calculate quantity to buy based on available funds
        if quantity is None:
            available_usd = wallet.usd_balance * 0.5  # Use 50% of wallet
            quantity = available_usd / opportunity.buy_price
        
        # Execute buy trade
        buy_trade = self._execute_buy(wallet, opportunity, quantity)
        if not buy_trade:
            return None
        
        # Execute sell trade immediately (simulation)
        sell_trade = self._execute_sell(wallet, opportunity, quantity, buy_trade.price)
        
        if sell_trade:
            # Calculate profit
            profit_loss = sell_trade.net_cost - buy_trade.net_cost
            profit_loss_percent = (profit_loss / buy_trade.net_cost) * 100 if buy_trade.net_cost != 0 else 0
            
            sell_trade.profit_loss = profit_loss
            sell_trade.profit_loss_percent = profit_loss_percent
            sell_trade.opportunity_id = opportunity.id
            
            wallet.total_profit_loss += profit_loss
            
            db.session.commit()
            
            return {
                'buy_trade': buy_trade,
                'sell_trade': sell_trade,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent
            }
        
        return None
    
    def _execute_buy(self, wallet, opportunity, quantity):
        """Execute buy trade"""
        try:
            total_cost = quantity * opportunity.buy_price
            fee = total_cost * self.fee
            net_cost = total_cost + fee
            
            if not wallet.can_afford(net_cost):
                return None
            
            # Deduct from wallet
            wallet.withdraw_funds(net_cost)
            wallet.total_invested += net_cost
            
            # Create trade record
            trade = Trade(
                wallet_id=wallet.id,
                trading_pair=opportunity.trading_pair,
                trade_type='BUY',
                exchange=opportunity.buy_exchange,
                quantity=quantity,
                price=opportunity.buy_price,
                total_cost=total_cost,
                fee=fee,
                net_cost=net_cost,
                status='completed'
            )
            
            db.session.add(trade)
            db.session.flush()
            
            return trade
        except Exception as e:
            print(f"Error executing buy trade: {e}")
            db.session.rollback()
            return None
    
    def _execute_sell(self, wallet, opportunity, quantity, buy_price):
        """Execute sell trade"""
        try:
            total_revenue = quantity * opportunity.sell_price
            fee = total_revenue * self.fee
            net_revenue = total_revenue - fee
            
            # Add to wallet
            wallet.add_funds(net_revenue)
            
            # Create trade record
            trade = Trade(
                wallet_id=wallet.id,
                trading_pair=opportunity.trading_pair,
                trade_type='SELL',
                exchange=opportunity.sell_exchange,
                quantity=quantity,
                price=opportunity.sell_price,
                total_cost=total_revenue,
                fee=fee,
                net_cost=net_revenue,
                status='completed'
            )
            
            db.session.add(trade)
            db.session.flush()
            
            return trade
        except Exception as e:
            print(f"Error executing sell trade: {e}")
            db.session.rollback()
            return None
    
    def get_wallet_stats(self):
        """Get wallet statistics"""
        wallet = self.get_or_create_wallet()
        
        return {
            'usd_balance': wallet.usd_balance,
            'total_invested': wallet.total_invested,
            'total_profit_loss': wallet.total_profit_loss,
            'total_portfolio_value': wallet.get_total_value(),
            'roi_percent': (wallet.total_profit_loss / wallet.total_invested * 100) if wallet.total_invested > 0 else 0
        }

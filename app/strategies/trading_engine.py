"""
Paper trading engine with optimized order execution pipeline
"""

import time
from app import db
from app.models.wallet import Wallet, Holding
from app.models.trade import Trade
from app.latency.order_queue import order_queue
from app.latency.metrics import latency_tracker
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
        Execute a simulated arbitrage trade with optimized latency.
        
        Uses pre-prepared orders for sub-50ms execution.
        
        Args:
            opportunity: Opportunity object
            quantity: Amount of crypto to buy (if None, calculate from wallet)
        
        Returns: Trade object or None if failed
        """
        cycle_start = time.time()
        latency_tracker.start_phase('order_preparation')
        
        wallet = self.get_or_create_wallet()
        
        if not wallet.can_afford(opportunity.buy_price):
            print(f"❌ Insufficient funds for {opportunity.trading_pair}")
            return None
        
        # Calculate quantity to buy based on available funds
        if quantity is None:
            available_usd = wallet.usd_balance * 0.5  # Use 50% of wallet
            quantity = available_usd / opportunity.buy_price
        
        # Prepare orders (no API calls yet)
        buy_order = order_queue.prepare_buy_order(
            exchange=opportunity.buy_exchange,
            symbol=opportunity.trading_pair,
            quantity=quantity,
            price=opportunity.buy_price
        )
        
        sell_order = order_queue.prepare_sell_order(
            exchange=opportunity.sell_exchange,
            symbol=opportunity.trading_pair,
            quantity=quantity,
            price=opportunity.sell_price
        )
        
        latency_tracker.end_phase('order_preparation')
        
        # Submit orders
        latency_tracker.start_phase('order_submission')
        
        if not order_queue.submit_order(buy_order):
            print(f"❌ Failed to queue buy order")
            return None
        
        if not order_queue.submit_order(sell_order):
            print(f"❌ Failed to queue sell order")
            return None
        
        latency_tracker.end_phase('order_submission')
        
        # Execute trades (simulated)
        buy_trade = self._execute_buy(wallet, opportunity, quantity, buy_order)
        if not buy_trade:
            return None
        
        sell_trade = self._execute_sell(wallet, opportunity, quantity, buy_trade.price, sell_order)
        
        if sell_trade:
            # Record fill confirmation
            latency_tracker.start_phase('order_confirmation')
            order_queue.mark_filled(buy_order.order_id)
            order_queue.mark_filled(sell_order.order_id)
            latency_tracker.end_phase('order_confirmation')
            
            # Calculate profit
            profit_loss = sell_trade.net_cost - buy_trade.net_cost
            profit_loss_percent = (profit_loss / buy_trade.net_cost) * 100 if buy_trade.net_cost != 0 else 0
            
            sell_trade.profit_loss = profit_loss
            sell_trade.profit_loss_percent = profit_loss_percent
            sell_trade.opportunity_id = opportunity.id
            
            wallet.total_profit_loss += profit_loss
            
            db.session.commit()
            
            # Log execution metrics
            cycle_time = (time.time() - cycle_start) * 1000
            print(f"✅ Trade executed in {cycle_time:.1f}ms")
            
            return {
                'buy_trade': buy_trade,
                'sell_trade': sell_trade,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent,
                'execution_time_ms': cycle_time,
                'buy_order_id': buy_order.order_id,
                'sell_order_id': sell_order.order_id
            }
        
        return None
    
    def _execute_buy(self, wallet, opportunity, quantity, order):
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
    
    def _execute_sell(self, wallet, opportunity, quantity, buy_price, order):
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

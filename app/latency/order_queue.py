"""
Pre-execution order pipeline for sub-50ms order placement.
Orders are prepared in advance and submitted instantly when conditions met.
"""

import time
from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum


class OrderStatus(Enum):
    """Order lifecycle states"""
    PREPARED = "prepared"  # Ready to submit
    PENDING = "pending"    # Submitted, awaiting confirmation
    FILLED = "filled"      # Executed successfully
    REJECTED = "rejected"  # Exchange rejected
    CANCELLED = "cancelled"


@dataclass
class PreparedOrder:
    """
    Pre-signed order ready for instant execution.
    Created during detection phase, submitted during execution phase.
    """
    
    order_id: str
    exchange: str
    side: str  # 'buy' or 'sell'
    symbol: str
    quantity: float
    price: float
    timestamp: float
    
    status: OrderStatus = OrderStatus.PREPARED
    submitted_at: Optional[float] = None
    filled_at: Optional[float] = None
    execution_time_ms: Optional[float] = None
    
    def mark_submitted(self):
        """Record when order was sent to exchange"""
        self.status = OrderStatus.PENDING
        self.submitted_at = time.time()
    
    def mark_filled(self):
        """Record when order was filled"""
        self.status = OrderStatus.FILLED
        self.filled_at = time.time()
        if self.submitted_at:
            self.execution_time_ms = (self.filled_at - self.submitted_at) * 1000
    
    def mark_rejected(self):
        """Record rejection"""
        self.status = OrderStatus.REJECTED
    
    def time_to_submit_ms(self) -> float:
        """Get milliseconds since order was prepared"""
        return (time.time() - self.timestamp) * 1000
    
    def is_stale(self, max_age_ms: float = 5000) -> bool:
        """Check if order is too old to submit"""
        return self.time_to_submit_ms() > max_age_ms


class OrderQueue:
    """
    FIFO queue of prepared orders ready for execution.
    Enables instant submission without building order during detection.
    """
    
    def __init__(self, max_queue_size: int = 1000):
        self.queue = []
        self.max_size = max_queue_size
        self.metrics = {
            'total_prepared': 0,
            'total_submitted': 0,
            'total_filled': 0,
            'avg_latency_ms': 0,
            'rejected': 0
        }
        self._submitted_orders = {}  # Track by order_id
    
    def prepare_buy_order(
        self,
        exchange: str,
        symbol: str,
        quantity: float,
        price: float
    ) -> Optional[PreparedOrder]:
        """
        Pre-create buy order (no API call yet).
        Returns order object ready to submit instantly.
        """
        if len(self.queue) >= self.max_size:
            print(f"⚠️  Order queue full ({self.max_size}), dropping oldest order")
            self.queue.pop(0)
        
        order = PreparedOrder(
            order_id=f"BUY-{exchange}-{symbol}-{int(time.time()*1000)}",
            exchange=exchange,
            side='buy',
            symbol=symbol,
            quantity=quantity,
            price=price,
            timestamp=time.time()
        )
        
        self.queue.append(order)
        self.metrics['total_prepared'] += 1
        
        return order
    
    def prepare_sell_order(
        self,
        exchange: str,
        symbol: str,
        quantity: float,
        price: float
    ) -> Optional[PreparedOrder]:
        """Pre-create sell order."""
        if len(self.queue) >= self.max_size:
            self.queue.pop(0)
        
        order = PreparedOrder(
            order_id=f"SELL-{exchange}-{symbol}-{int(time.time()*1000)}",
            exchange=exchange,
            side='sell',
            symbol=symbol,
            quantity=quantity,
            price=price,
            timestamp=time.time()
        )
        
        self.queue.append(order)
        self.metrics['total_prepared'] += 1
        
        return order
    
    def submit_order(self, order: PreparedOrder) -> bool:
        """
        Mark order as submitted (actual exchange call happens in trading_engine).
        This just records the submission time for latency tracking.
        """
        if order.is_stale():
            print(f"⚠️  Order {order.order_id} stale ({order.time_to_submit_ms():.1f}ms old)")
            order.mark_rejected()
            self.metrics['rejected'] += 1
            return False
        
        order.mark_submitted()
        self._submitted_orders[order.order_id] = order
        self.metrics['total_submitted'] += 1
        
        return True
    
    def mark_filled(self, order_id: str) -> Optional[Dict]:
        """
        Record order as filled and return execution metrics.
        """
        if order_id not in self._submitted_orders:
            return None
        
        order = self._submitted_orders[order_id]
        order.mark_filled()
        self.metrics['total_filled'] += 1
        
        # Update average latency
        if order.execution_time_ms:
            total_ms = self.metrics['avg_latency_ms'] * (self.metrics['total_filled'] - 1)
            self.metrics['avg_latency_ms'] = (
                (total_ms + order.execution_time_ms) / self.metrics['total_filled']
            )
        
        return {
            'order_id': order_id,
            'execution_time_ms': order.execution_time_ms,
            'filled_at': order.filled_at
        }
    
    def get_pending_orders(self) -> list:
        """Get all orders awaiting submission"""
        return [o for o in self.queue if o.status == OrderStatus.PREPARED]
    
    def get_submitted_orders(self) -> list:
        """Get all orders that were submitted but not yet filled"""
        return [o for o in self._submitted_orders.values() if o.status == OrderStatus.PENDING]
    
    def get_metrics(self) -> Dict:
        """Return execution metrics"""
        return {
            **self.metrics,
            'queue_size': len(self.queue),
            'pending_submissions': len(self.get_pending_orders()),
            'avg_latency_ms': round(self.metrics['avg_latency_ms'], 2)
        }
    
    def clear(self):
        """Clear all orders"""
        self.queue.clear()
        self._submitted_orders.clear()


# Global order queue instance
order_queue = OrderQueue()

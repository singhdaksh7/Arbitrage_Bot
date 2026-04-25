"""
In-memory price cache for sub-millisecond lookup during detection phase
"""

import time
from collections import defaultdict
from threading import RLock


class PriceCache:
    """
    Thread-safe in-memory price cache.
    Eliminates database queries during detection phase.
    """
    
    def __init__(self, max_age_seconds=5):
        """
        Args:
            max_age_seconds: Invalidate prices older than this
        """
        self.cache = defaultdict(dict)  # {exchange: {pair: {bid, ask, timestamp}}}
        self.lock = RLock()
        self.max_age = max_age_seconds
        self.stats = {'hits': 0, 'misses': 0, 'stale': 0}
    
    def set(self, exchange, pair, bid, ask, timestamp=None):
        """Store price in cache"""
        with self.lock:
            self.cache[exchange][pair] = {
                'bid': bid,
                'ask': ask,
                'timestamp': timestamp or time.time()
            }
    
    def get(self, exchange, pair):
        """
        Retrieve price if fresh, else None.
        Returns: {'bid': float, 'ask': float} or None
        """
        with self.lock:
            if exchange not in self.cache or pair not in self.cache[exchange]:
                self.stats['misses'] += 1
                return None
            
            data = self.cache[exchange][pair]
            age = time.time() - data['timestamp']
            
            if age > self.max_age:
                self.stats['stale'] += 1
                return None
            
            self.stats['hits'] += 1
            return {'bid': data['bid'], 'ask': data['ask']}
    
    def get_all_for_pair(self, pair):
        """Get prices from all exchanges for a trading pair"""
        with self.lock:
            result = {}
            for exchange, pairs in self.cache.items():
                if pair in pairs:
                    data = pairs[pair]
                    age = time.time() - data['timestamp']
                    if age <= self.max_age:
                        result[exchange] = {
                            'bid': data['bid'],
                            'ask': data['ask']
                        }
            return result
    
    def clear(self):
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()
    
    def invalidate_exchange(self, exchange):
        """Clear data for single exchange"""
        with self.lock:
            if exchange in self.cache:
                del self.cache[exchange]
    
    def get_stats(self):
        """Return cache hit/miss statistics"""
        with self.lock:
            return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistics counters"""
        with self.lock:
            self.stats = {'hits': 0, 'misses': 0, 'stale': 0}


# Global cache instance
price_cache = PriceCache(max_age_seconds=3)

"""
Base exchange connector class
"""

import ccxt
from abc import ABC, abstractmethod

class ExchangeConnector(ABC):
    """Base class for exchange connectors"""
    
    def __init__(self, exchange_name):
        self.exchange_name = exchange_name
        self.exchange = None
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Initialize CCXT exchange"""
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            self.exchange = exchange_class({'enableRateLimit': True})
            print(f"✓ {self.exchange_name.capitalize()} initialized")
        except Exception as e:
            print(f"✗ Failed to initialize {self.exchange_name}: {e}")
    
    def get_price(self, trading_pair):
        """
        Get current price for a trading pair
        Returns: {'bid': float, 'ask': float, 'last': float}
        """
        try:
            if not self.exchange:
                return None
            
            ticker = self.exchange.fetch_ticker(trading_pair)
            return {
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'last': ticker.get('last'),
                'timestamp': ticker.get('timestamp')
            }
        except Exception as e:
            print(f"✗ Error fetching {trading_pair} from {self.exchange_name}: {e}")
            return None
    
    def get_symbol(self, trading_pair):
        """Normalize trading pair symbol for the exchange"""
        try:
            if self.exchange:
                symbols = self.exchange.symbols
                # Try exact match
                if trading_pair in symbols:
                    return trading_pair
                # Try normalization
                normalized = trading_pair.replace('/', ':')
                if normalized in symbols:
                    return normalized
        except Exception as e:
            print(f"Error getting symbol: {e}")
        return trading_pair
    
    def is_available(self):
        """Check if exchange connector is available"""
        return self.exchange is not None

"""
Kraken exchange connector
"""

from app.exchanges.base_connector import ExchangeConnector

class KrakenConnector(ExchangeConnector):
    """Kraken exchange connector"""
    
    def __init__(self):
        super().__init__('kraken')
        self.supported_pairs = ['BTC/USD', 'ETH/USD', 'LTC/USD', 'ADA/USD', 'XRP/USD']
    
    def get_supported_pairs(self):
        """Get supported trading pairs"""
        return self.supported_pairs

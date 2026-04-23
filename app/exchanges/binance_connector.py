"""
Binance exchange connector
"""

from app.exchanges.base_connector import ExchangeConnector

class BinanceConnector(ExchangeConnector):
    """Binance exchange connector"""
    
    def __init__(self):
        super().__init__('binance')
        self.supported_pairs = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT', 'ADA/USDT', 'XRP/USDT']
    
    def get_supported_pairs(self):
        """Get supported trading pairs"""
        return self.supported_pairs

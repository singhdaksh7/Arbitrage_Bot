"""
Configuration file for Arbitrage Bot
"""

import os
from datetime import timedelta

# Determine database path
if os.environ.get('RENDER'):
    # Running on Render - use /tmp (writable directory)
    db_path = 'sqlite:////tmp/arbitrage_bot.db'
else:
    # Local development - use instance folder
    db_path = 'sqlite:///instance/arbitrage_bot.db'

class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    
    # Bot configuration
    INITIAL_WALLET_BALANCE = 1000  # $1000 virtual USD
    SCAN_INTERVAL = 1  # Reduced from 300s to 1s for sub-second detection
    UPDATE_INTERVAL = 60  # Seconds between price updates
    
    # Trading configuration
    MIN_PROFIT_PERCENTAGE = 1.5  # Minimum 1.5% profit (lowered for more opportunities)
    MAX_PROFIT_PERCENTAGE = 50.0  # Maximum profit % (filter out suspicious deals)
    TRANSACTION_FEE = 0.001  # 0.1% per transaction (typical exchange fee)
    
    # Advanced trading pairs (50+ coins across major categories)
    TRADING_PAIRS = [
        # Top 10 by market cap
        'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'ADA/USD',
        'SOL/USD', 'DOGE/USD', 'POLKADOT/USD', 'LTC/USD', 'AVAX/USD',
        # Layer 2 & Scaling
        'ARBITRUM/USD', 'OPTIMISM/USD', 'POLYGON/USD', 'STARKNET/USD',
        # DeFi Tokens
        'AAVE/USD', 'UNISWAP/USD', 'CURVE/USD', 'BALANCER/USD', 'LIDO/USD',
        # Stablecoins & Wrapped
        'USDC/USD', 'USDT/USD', 'DAI/USD', 'WBTC/USD', 'WETH/USD',
        # Altcoins with high volume
        'CHAINLINK/USD', 'COSMOS/USD', 'HELIUM/USD', 'NEAR/USD', 'FLOW/USD',
        'FILECOIN/USD', 'THE GRAPH/USD', 'ENS/USD', 'MAKER/USD', 'COMPOUND/USD',
    ]
    
    # Exchanges
    EXCHANGES = ['binance', 'kraken']
    
    # Alerts configuration
    ENABLE_ALERTS = True
    ALERT_MIN_PROFIT = 2.5  # Alert if opportunity > 2.5%
    
    # Backtesting configuration
    BACKTEST_DAYS = 7  # Historical data for backtesting
    
    # Latency optimization
    ENABLE_ASYNC_FETCHING = True  # Use parallel API calls
    ENABLE_PRICE_CACHE = True    # Use in-memory price cache
    ENABLE_ORDER_QUEUE = True     # Use pre-prepared orders
    LATENCY_TRACKING = True        # Track execution latency metrics

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

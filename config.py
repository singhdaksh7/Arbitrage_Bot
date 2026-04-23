"""
Configuration file for Arbitrage Bot
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///arbitrage_bot.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    
    # Bot configuration
    INITIAL_WALLET_BALANCE = 1000  # $1000 virtual USD
    UPDATE_INTERVAL = 60  # Seconds between price updates
    
    # Trading configuration
    MIN_PROFIT_PERCENTAGE = 2.0  # Minimum 2% profit to consider
    TRANSACTION_FEE = 0.001  # 0.1% per transaction (typical exchange fee)
    
    # Supported pairs (can add more)
    TRADING_PAIRS = ['BTC/USD', 'ETH/USD', 'LTC/USD']
    
    # Exchanges
    EXCHANGES = ['binance', 'kraken']

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

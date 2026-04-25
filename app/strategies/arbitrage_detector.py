"""
Arbitrage detection strategy with parallel price fetching
"""

import asyncio
import time
from app import db
from app.models.opportunity import Opportunity
from app.latency.async_fetcher import AsyncPriceFetcher
from app.latency.metrics import latency_tracker
from app.latency.order_queue import order_queue
from config import Config

class ArbitrageDetector:
    """Detects arbitrage opportunities between exchanges"""
    
    def __init__(self, exchanges):
        """
        Initialize detector with exchange connectors
        exchanges: dict of {exchange_name: connector}
        """
        self.exchanges = exchanges
        self.min_profit_percent = Config.MIN_PROFIT_PERCENTAGE
        self.fee = Config.TRANSACTION_FEE
        self.async_fetcher = AsyncPriceFetcher(exchanges)
    
    def detect_opportunities(self, trading_pairs):
        """
        Detect arbitrage opportunities across exchanges (ASYNC VERSION).
        
        Returns: list of Opportunity objects
        """
        cycle_start = time.time()
        latency_tracker.start_phase('full_detection_cycle')
        
        # Fetch prices in parallel (not sequential)
        latency_tracker.start_phase('price_fetch')
        try:
            prices = asyncio.run(self.async_fetcher.fetch_prices_parallel(trading_pairs))
        except RuntimeError:
            # Fallback if no event loop
            prices = self._fetch_prices_sync(trading_pairs)
        latency_tracker.end_phase('price_fetch')
        
        if not prices:
            return []
        
        # Compare and find opportunities
        latency_tracker.start_phase('comparison')
        opportunities = []
        for pair in trading_pairs:
            pair_prices = {ex: prices.get(ex, {}).get(pair) for ex in prices}
            pair_prices = {k: v for k, v in pair_prices.items() if v}
            
            if len(pair_prices) < 2:
                continue
            
            opps = self._compare_prices(pair, pair_prices)
            opportunities.extend(opps)
        latency_tracker.end_phase('comparison')
        
        # Record cycle time
        cycle_time = (time.time() - cycle_start) * 1000
        latency_tracker.record_full_cycle(cycle_time)
        
        return opportunities
    
    def _fetch_prices_sync(self, trading_pairs):
        """Fallback sequential price fetch"""
        prices = {}
        for pair in trading_pairs:
            for exchange_name, connector in self.exchanges.items():
                if not connector.is_available():
                    continue
                try:
                    price_data = connector.get_price(pair)
                    if price_data and price_data.get('ask'):
                        if exchange_name not in prices:
                            prices[exchange_name] = {}
                        prices[exchange_name][pair] = {
                            'ask': price_data['ask'],
                            'bid': price_data['bid']
                        }
                except Exception as e:
                    print(f"Error fetching {pair} from {exchange_name}: {e}")
        return prices
    
    def _compare_prices(self, trading_pair, prices):
        """Compare prices and find arbitrage opportunities"""
        opportunities = []
        exchange_names = list(prices.keys())
        
        # Compare all pairs of exchanges
        for i in range(len(exchange_names)):
            for j in range(i + 1, len(exchange_names)):
                ex1, ex2 = exchange_names[i], exchange_names[j]
                
                # Check if buying from ex1 and selling at ex2 is profitable
                opp1 = self._check_opportunity(
                    trading_pair, ex1, ex2, 
                    prices[ex1]['ask'], prices[ex2]['bid']
                )
                if opp1:
                    opportunities.append(opp1)
                
                # Check if buying from ex2 and selling at ex1 is profitable
                opp2 = self._check_opportunity(
                    trading_pair, ex2, ex1, 
                    prices[ex2]['ask'], prices[ex1]['bid']
                )
                if opp2:
                    opportunities.append(opp2)
        
        return opportunities
    
    def _check_opportunity(self, trading_pair, buy_exchange, sell_exchange, buy_price, sell_price):
        """Check if an opportunity is profitable after fees"""
        if buy_price is None or sell_price is None or buy_price == 0:
            return None
        
        # Calculate profit/loss
        price_diff = sell_price - buy_price
        price_diff_percent = (price_diff / buy_price) * 100
        
        # Account for fees (buy fee and sell fee)
        total_fee_percent = self.fee * 2 * 100  # Fee as percentage
        profit_after_fees = price_diff_percent - total_fee_percent
        
        # Only consider if profitable
        if profit_after_fees >= self.min_profit_percent:
            opportunity = Opportunity(
                trading_pair=trading_pair,
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                buy_price=buy_price,
                sell_price=sell_price,
                price_difference=price_diff,
                price_difference_percent=price_diff_percent,
                profit_after_fees=profit_after_fees,
                profit_percent=profit_after_fees,
                is_active=True
            )
            return opportunity
        
        return None
    
    def save_opportunities(self, opportunities):
        """Save opportunities to database"""
        try:
            for opp in opportunities:
                # Check if similar opportunity already exists
                existing = Opportunity.query.filter_by(
                    trading_pair=opp.trading_pair,
                    buy_exchange=opp.buy_exchange,
                    sell_exchange=opp.sell_exchange,
                    is_executed=False
                ).order_by(Opportunity.detected_at.desc()).first()
                
                # Only save if new or significant price change
                if not existing or abs(existing.profit_percent - opp.profit_percent) > 0.5:
                    db.session.add(opp)
            
            db.session.commit()
            return len(opportunities)
        except Exception as e:
            db.session.rollback()
            print(f"Error saving opportunities: {e}")
            return 0

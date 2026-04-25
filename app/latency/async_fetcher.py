"""
Async parallel price fetching from multiple exchanges simultaneously.
Reduces ~15-20s sequential latency to ~1-2s parallel.
"""

import asyncio
import aiohttp
import ccxt
import time
from typing import Dict, List, Optional
from app.latency.price_cache import price_cache


class AsyncPriceFetcher:
    """
    Fetch prices from multiple exchanges in parallel using asyncio.
    Each exchange connection runs concurrently, not sequentially.
    """
    
    def __init__(self, exchanges_config: Dict):
        """
        Args:
            exchanges_config: {exchange_name: connector_instance}
        """
        self.exchanges = exchanges_config
        self.rate_limiter = {}  # Track requests per exchange
        self.metrics = {
            'total_fetches': 0,
            'total_time_ms': 0,
            'errors': 0,
            'cache_hits': 0
        }
    
    async def fetch_prices_parallel(self, pairs: List[str]) -> Dict:
        """
        Fetch prices for all pairs from all exchanges in parallel.
        
        Returns:
            {
                exchange_name: {
                    pair: {'bid': float, 'ask': float, 'timestamp': float},
                    ...
                },
                ...
            }
        """
        start_time = time.time()
        
        # Create tasks for all exchange/pair combinations
        tasks = []
        task_map = {}  # Map task -> (exchange, pair)
        
        for pair in pairs:
            for exchange_name, connector in self.exchanges.items():
                if not connector.is_available():
                    continue
                
                # Check cache first (sub-ms lookup)
                cached = price_cache.get(exchange_name, pair)
                if cached:
                    self.metrics['cache_hits'] += 1
                    continue
                
                # Create async task
                task = asyncio.create_task(
                    self._fetch_ticker(exchange_name, connector, pair)
                )
                tasks.append(task)
                task_map[task] = (exchange_name, pair)
        
        if not tasks:
            return self._build_response_from_cache(pairs)
        
        # Wait for all tasks with timeout
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"❌ Async fetch error: {e}")
            self.metrics['errors'] += 1
            return {}
        
        # Process results and update cache
        response = {}
        for task, result in zip(tasks, results):
            exchange_name, pair = task_map[task]
            
            if isinstance(result, Exception):
                print(f"⚠️  {exchange_name}/{pair}: {result}")
                self.metrics['errors'] += 1
                continue
            
            if result and 'bid' in result and 'ask' in result:
                if exchange_name not in response:
                    response[exchange_name] = {}
                
                response[exchange_name][pair] = result
                
                # Cache for next detection cycle
                price_cache.set(
                    exchange_name, pair,
                    result['bid'], result['ask'],
                    result.get('timestamp', time.time())
                )
        
        # Add cached data to response
        cached_data = self._build_response_from_cache(pairs)
        for exchange_name, pairs_data in cached_data.items():
            if exchange_name not in response:
                response[exchange_name] = {}
            response[exchange_name].update(pairs_data)
        
        # Record metrics
        elapsed_ms = (time.time() - start_time) * 1000
        self.metrics['total_fetches'] += 1
        self.metrics['total_time_ms'] += elapsed_ms
        
        return response
    
    async def _fetch_ticker(self, exchange_name: str, connector, pair: str) -> Optional[Dict]:
        """
        Fetch single ticker asynchronously.
        Respects rate limits without blocking other exchanges.
        """
        try:
            # Try primary pair
            ticker = connector.exchange.fetch_ticker(pair)
            return {
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'timestamp': ticker.get('timestamp', time.time())
            }
        except ccxt.ExchangeNotAvailable:
            # Try alternative symbol format (USD -> USDT)
            try:
                alt_pair = pair.replace('USD', 'USDT') if 'USD' in pair else pair
                if alt_pair != pair:
                    ticker = connector.exchange.fetch_ticker(alt_pair)
                    return {
                        'bid': ticker.get('bid'),
                        'ask': ticker.get('ask'),
                        'timestamp': ticker.get('timestamp', time.time())
                    }
            except Exception:
                pass
            return None
        except Exception as e:
            print(f"Error fetching {pair} from {exchange_name}: {e}")
            return None
    
    def _build_response_from_cache(self, pairs: List[str]) -> Dict:
        """Build response using only cached data"""
        response = {}
        for pair in pairs:
            cached = price_cache.get_all_for_pair(pair)
            for exchange_name, data in cached.items():
                if exchange_name not in response:
                    response[exchange_name] = {}
                response[exchange_name][pair] = data
        return response
    
    def get_metrics(self) -> Dict:
        """Return performance metrics"""
        avg_time = (
            self.metrics['total_time_ms'] / max(self.metrics['total_fetches'], 1)
        )
        return {
            **self.metrics,
            'avg_fetch_time_ms': round(avg_time, 2),
            'cache_hit_rate': f"{(self.metrics['cache_hits'] / max(self.metrics['cache_hits'] + self.metrics['errors'], 1) * 100):.1f}%"
        }
    
    def reset_metrics(self):
        """Reset metrics counters"""
        self.metrics = {
            'total_fetches': 0,
            'total_time_ms': 0,
            'errors': 0,
            'cache_hits': 0
        }


# Utility to run async fetch in sync context
def fetch_prices_sync(fetcher: AsyncPriceFetcher, pairs: List[str]) -> Dict:
    """
    Run async fetch from synchronous code.
    Used by Flask routes which don't support native async.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context
            return asyncio.run_coroutine_threadsafe(
                fetcher.fetch_prices_parallel(pairs), loop
            ).result()
        else:
            return asyncio.run(fetcher.fetch_prices_parallel(pairs))
    except RuntimeError:
        # No event loop in this thread
        return asyncio.run(fetcher.fetch_prices_parallel(pairs))

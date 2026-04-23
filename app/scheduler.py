"""
Background task scheduler for automated scanning
"""

from apscheduler.schedulers.background import BackgroundScheduler
from app.strategies.arbitrage_detector import ArbitrageDetector
from app.strategies.trading_engine import TradingEngine
from app.models.opportunity import Opportunity
from app.models.price import PriceSnapshot
from app import db
from config import Config
import logging

logger = logging.getLogger(__name__)

class BotScheduler:
    """Manages background tasks"""
    
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.detector = None
        
    def init_app(self, app):
        """Initialize scheduler with Flask app"""
        self.app = app
        self.detector = ArbitrageDetector()
        
    def start(self):
        """Start background scheduler"""
        if not self.scheduler.running:
            self.scheduler.add_job(
                self.scan_opportunities,
                'interval',
                seconds=Config.SCAN_INTERVAL,
                id='arbitrage_scan'
            )
            self.scheduler.start()
            logger.info("✅ Background scanner started")
    
    def stop(self):
        """Stop background scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⏹️ Background scanner stopped")
    
    def scan_opportunities(self):
        """Run automated opportunity scan"""
        try:
            with self.app.app_context():
                opportunities = self.detector.scan_opportunities()
                
                # Save to database
                for opp in opportunities:
                    existing = Opportunity.query.filter_by(
                        exchange_from=opp['exchange_from'],
                        exchange_to=opp['exchange_to'],
                        pair=opp['pair']
                    ).first()
                    
                    if not existing:
                        db.session.add(Opportunity(**opp))
                
                db.session.commit()
                logger.info(f"🔍 Found {len(opportunities)} opportunities")
                
        except Exception as e:
            logger.error(f"❌ Scan error: {str(e)}")

scheduler = BotScheduler()

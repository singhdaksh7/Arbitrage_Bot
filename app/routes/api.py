"""
REST API endpoints
"""

from flask import jsonify, request, current_app
from app.routes import api_bp
from app.models.opportunity import Opportunity
from app.models.trade import Trade
from app.models.wallet import Wallet
from app.strategies.arbitrage_detector import ArbitrageDetector
from app.strategies.trading_engine import TradingEngine
from app.exchanges.binance_connector import BinanceConnector
from app.exchanges.kraken_connector import KrakenConnector
from config import Config

# Initialize connectors
exchanges = {
    'binance': BinanceConnector(),
    'kraken': KrakenConnector()
}
detector = ArbitrageDetector(exchanges)
engine = TradingEngine()

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get bot status"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'exchanges': list(exchanges.keys()),
        'tracking_pairs': Config.TRADING_PAIRS
    })

@api_bp.route('/opportunities', methods=['GET'])
def get_opportunities():
    """Get recent opportunities"""
    limit = request.args.get('limit', 50, type=int)
    active_only = request.args.get('active_only', True, type=bool)
    
    query = Opportunity.query
    if active_only:
        query = query.filter_by(is_active=True)
    
    opportunities = query.order_by(Opportunity.detected_at.desc()).limit(limit).all()
    
    return jsonify({
        'opportunities': [opp.to_dict() for opp in opportunities],
        'count': len(opportunities)
    })

@api_bp.route('/opportunities/scan', methods=['POST'])
def scan_opportunities():
    """Manually trigger opportunity scan"""
    try:
        opportunities = detector.detect_opportunities(Config.TRADING_PAIRS)
        saved_count = detector.save_opportunities(opportunities)
        
        return jsonify({
            'success': True,
            'detected': len(opportunities),
            'saved': saved_count,
            'opportunities': [opp.to_dict() if hasattr(opp, 'to_dict') else {} for opp in opportunities[:10]]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/trades', methods=['GET'])
def get_trades():
    """Get recent trades"""
    limit = request.args.get('limit', 50, type=int)
    trades = Trade.query.order_by(Trade.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'trades': [trade.to_dict() for trade in trades],
        'count': len(trades)
    })

@api_bp.route('/trades/execute', methods=['POST'])
def execute_trade():
    """Execute a trade on an opportunity"""
    try:
        data = request.get_json()
        opportunity_id = data.get('opportunity_id')
        quantity = data.get('quantity')
        
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return jsonify({'success': False, 'error': 'Opportunity not found'}), 404
        
        result = engine.execute_trade(opportunity, quantity)
        
        if result:
            return jsonify({
                'success': True,
                'buy_trade': result['buy_trade'].to_dict(),
                'sell_trade': result['sell_trade'].to_dict(),
                'profit_loss': result['profit_loss'],
                'profit_loss_percent': result['profit_loss_percent']
            })
        else:
            return jsonify({'success': False, 'error': 'Trade execution failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/wallet', methods=['GET'])
def get_wallet():
    """Get wallet information and statistics"""
    stats = engine.get_wallet_stats()
    wallet = Wallet.query.first()
    
    return jsonify({
        'wallet': {
            'id': wallet.id if wallet else None,
            'usd_balance': stats['usd_balance'],
            'total_invested': stats['total_invested'],
            'total_profit_loss': stats['total_profit_loss'],
            'total_portfolio_value': stats['total_portfolio_value'],
            'roi_percent': stats['roi_percent'],
            'created_at': wallet.created_at.isoformat() if wallet else None
        }
    })

@api_bp.route('/wallet/reset', methods=['POST'])
def reset_wallet():
    """Reset wallet to initial state"""
    try:
        from app import db
        
        # Delete all trades and opportunities
        Trade.query.delete()
        Opportunity.query.delete()
        Wallet.query.delete()
        db.session.commit()
        
        # Create new wallet
        engine.get_or_create_wallet()
        
        return jsonify({'success': True, 'message': 'Wallet reset successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    wallet = Wallet.query.first()
    
    total_trades = Trade.query.count()
    total_opportunities = Opportunity.query.count()
    executed_opportunities = Opportunity.query.filter_by(is_executed=True).count()
    
    trades_data = Trade.query.all()
    total_fees_paid = sum(t.fee for t in trades_data) if trades_data else 0
    
    return jsonify({
        'wallet': engine.get_wallet_stats() if wallet else {},
        'trades': {
            'total': total_trades,
            'total_fees_paid': total_fees_paid
        },
        'opportunities': {
            'total_detected': total_opportunities,
            'executed': executed_opportunities,
            'pending': total_opportunities - executed_opportunities
        }
    })

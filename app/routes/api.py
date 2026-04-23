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

@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get recent alerts"""
    from app.alerts import alert_manager
    limit = request.args.get('limit', 20, type=int)
    alerts = alert_manager.get_alerts(limit)
    return jsonify({'alerts': alerts})

@api_bp.route('/backtesting/run', methods=['POST'])
def run_backtest():
    """Run backtesting simulation"""
    from app.backtester import backtest_engine
    
    days = request.json.get('days', 7) if request.json else 7
    initial_balance = request.json.get('initial_balance', 1000) if request.json else 1000
    
    results = backtest_engine.backtest(days, initial_balance)
    return jsonify(results)

@api_bp.route('/opportunities/filtered', methods=['GET'])
def get_filtered_opportunities():
    """Get opportunities with advanced filters"""
    min_profit = request.args.get('min_profit', 1.5, type=float)
    max_profit = request.args.get('max_profit', 50, type=float)
    exchange_from = request.args.get('exchange_from', type=str)
    limit = request.args.get('limit', 50, type=int)
    
    query = Opportunity.query.filter(
        Opportunity.profit_percentage.between(min_profit, max_profit)
    )
    
    if exchange_from:
        query = query.filter_by(exchange_from=exchange_from)
    
    opportunities = query.order_by(Opportunity.profit_percentage.desc()).limit(limit).all()
    
    return jsonify({
        'opportunities': [opp.to_dict() for opp in opportunities],
        'count': len(opportunities),
        'filters': {
            'min_profit': min_profit,
            'max_profit': max_profit,
            'exchange_from': exchange_from
        }
    })

@api_bp.route('/opportunities/top', methods=['GET'])
def get_top_opportunities():
    """Get top 10 most profitable opportunities"""
    limit = request.args.get('limit', 10, type=int)
    opportunities = Opportunity.query.filter_by(is_active=True).order_by(
        Opportunity.profit_percentage.desc()
    ).limit(limit).all()
    
    return jsonify({
        'opportunities': [opp.to_dict() for opp in opportunities],
        'count': len(opportunities)
    })

@api_bp.route('/performance', methods=['GET'])
def get_performance():
    """Get bot performance metrics"""
    trades = Trade.query.all()
    
    if not trades:
        return jsonify({
            'performance': {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_profit_per_trade': 0,
                'total_profit': 0
            }
        })
    
    winning = [t for t in trades if t.profit_loss > 0]
    losing = [t for t in trades if t.profit_loss < 0]
    
    total_profit = sum(t.profit_loss for t in trades)
    avg_profit = total_profit / len(trades) if trades else 0
    
    return jsonify({
        'performance': {
            'total_trades': len(trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(trades) * 100) if trades else 0,
            'avg_profit_per_trade': round(avg_profit, 2),
            'total_profit': round(total_profit, 2),
            'best_trade': max([t.profit_loss for t in trades]) if trades else 0,
            'worst_trade': min([t.profit_loss for t in trades]) if trades else 0
        }
    })

@api_bp.route('/opportunities/auto-scan', methods=['POST'])
def toggle_auto_scan():
    """Toggle automatic opportunity scanning"""
    from app.scheduler import scheduler
    
    enabled = request.json.get('enabled', True) if request.json else True
    
    try:
        if enabled:
            scheduler.start()
            message = "Auto-scan enabled - scanning every 5 minutes"
        else:
            scheduler.stop()
            message = "Auto-scan disabled"
        
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

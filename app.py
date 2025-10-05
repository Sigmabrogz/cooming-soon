"""
Polymarket Web Dashboard
------------------------
Flask web application for visualizing Polymarket data.
"""

from flask import Flask, render_template, jsonify, request
from polymarket import PolymarketClient
from whale_tracker import WhaleTracker
import os
import threading

app = Flask(__name__)
client = PolymarketClient()

# Initialize whale tracker
whale_tracker = WhaleTracker(min_trade_amount=10000)

# Start whale monitoring in background thread
def start_whale_monitoring():
    """Background thread for whale monitoring."""
    whale_tracker.run_monitor(interval=5)

monitor_thread = threading.Thread(target=start_whale_monitoring, daemon=True)
monitor_thread.start()


@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('dashboard.html')

@app.route('/whales')
def whales():
    """Render the whale activity page."""
    return render_template('whales.html')

@app.route('/markets')
def markets():
    """Render the markets page."""
    return render_template('markets.html')

@app.route('/analytics')
def analytics():
    """Render the analytics page."""
    return render_template('analytics.html')


@app.route('/api/markets')
def get_markets():
    """API endpoint to fetch top markets."""
    try:
        limit = int(request.args.get('limit', 20))
        markets = client.gamma.get_markets(
            closed=False,
            limit=limit,
            order="volume",
            ascending=False
        )
        
        # Clean up the data
        cleaned_markets = []
        for market in markets:
            cleaned_markets.append({
                'title': (market.get('question') or 
                         market.get('title') or 
                         market.get('slug', 'Unknown').replace('-', ' ').title()),
                'slug': market.get('slug', ''),
                'volume': float(market.get('volume', 0) or 0),
                'liquidity': float(market.get('liquidity', 0) or 0),
                'category': market.get('category', 'N/A'),
                'endDate': market.get('endDate', 'N/A'),
                'conditionId': market.get('conditionId', ''),
            })
        
        return jsonify({
            'success': True,
            'markets': cleaned_markets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/events')
def get_events():
    """API endpoint to fetch top events."""
    try:
        limit = int(request.args.get('limit', 10))
        events = client.gamma.get_events(
            closed=False,
            limit=limit,
            order="volume",
            ascending=False
        )
        
        # Clean up the data
        cleaned_events = []
        for event in events:
            cleaned_events.append({
                'title': (event.get('title') or 
                         event.get('name') or 
                         event.get('slug', 'Unknown').replace('-', ' ').title()),
                'slug': event.get('slug', ''),
                'volume': float(event.get('volume', 0) or 0),
                'liquidity': float(event.get('liquidity', 0) or 0),
                'startDate': event.get('startDate', 'N/A'),
                'endDate': event.get('endDate', 'N/A'),
            })
        
        return jsonify({
            'success': True,
            'events': cleaned_events
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/market/<slug>')
def get_market_details(slug):
    """API endpoint to fetch market details."""
    try:
        market = client.gamma.get_market_by_slug(slug)
        
        # Try to get holders
        try:
            condition_id = market.get('conditionId')
            holders_data = client.data.get_holders(market=condition_id, limit=10)
            if isinstance(holders_data, dict):
                holders = holders_data.get('holders', [])
            elif isinstance(holders_data, list):
                holders = holders_data
            else:
                holders = []
        except:
            holders = []
        
        return jsonify({
            'success': True,
            'market': market,
            'holders': holders
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats')
def get_stats():
    """API endpoint to fetch overall statistics."""
    try:
        markets = client.gamma.get_markets(closed=False, limit=100)
        
        total_volume = sum(float(m.get('volume', 0) or 0) for m in markets)
        total_liquidity = sum(float(m.get('liquidity', 0) or 0) for m in markets)
        active_markets = len(markets)
        
        return jsonify({
            'success': True,
            'stats': {
                'totalVolume': total_volume,
                'totalLiquidity': total_liquidity,
                'activeMarkets': active_markets,
                'avgVolume': total_volume / active_markets if active_markets > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/whale-activity')
def get_whale_activity():
    """API endpoint to fetch recent whale trades."""
    try:
        limit = int(request.args.get('limit', 20))
        whale_trades = whale_tracker.get_recent_whales(limit=limit)
        
        return jsonify({
            'success': True,
            'whales': whale_trades,
            'count': len(whale_trades)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/whale-activity/live')
def get_live_whale_activity():
    """API endpoint to check for new whale trades."""
    try:
        # This will return only NEW trades since last check
        new_whales = whale_tracker.check_for_new_whales()
        
        return jsonify({
            'success': True,
            'newWhales': new_whales,
            'count': len(new_whales)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = 8080
    print("\n" + "="*80)
    print("🚀 POLYMARKET WEB DASHBOARD")
    print("="*80)
    print(f"\n📊 Dashboard running at: http://localhost:{port}")
    print("🔄 Press Ctrl+C to stop\n")
    print("="*80 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=port)

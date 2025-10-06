"""
Polymarket Web Dashboard
------------------------
Flask web application for visualizing Polymarket data.
"""

from flask import Flask, render_template, jsonify, request
from polymarket import PolymarketClient
from polymarket.trader_analytics import TraderAnalytics
from polymarket.copy_trading import CopyTrading
from polymarket.data_engine import DataEngine
from whale_tracker import WhaleTracker
from datetime import datetime, timezone
import os
import threading

app = Flask(__name__)
client = PolymarketClient()

# Initialize whale tracker
whale_tracker = WhaleTracker(min_trade_amount=10000)

# Initialize new systems
trader_analytics = TraderAnalytics(client.data)
data_engine = DataEngine()
# Note: CopyTrading requires authenticated client for placing orders
# copy_trading = CopyTrading(client.clob, client.data)

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

@app.route('/traders')
def traders():
    """Render the traders/leaderboard page."""
    return render_template('traders.html')

@app.route('/trader/<wallet_address>')
def trader_profile(wallet_address):
    """Render individual trader profile page."""
    return render_template('trader_profile.html', wallet=wallet_address)

@app.route('/copy-trading')
def copy_trading_page():
    """Render the copy trading page."""
    return render_template('copy_trading.html')

@app.route('/how-to-bet')
def how_to_bet():
    """Render the betting guide page."""
    return render_template('how_to_bet.html')


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


@app.route('/api/dashboard/insights')
def get_dashboard_insights():
    """Provide actionable insights for the dashboard playbook."""
    def normalize_title(market_data):
        slug = market_data.get('slug', 'unknown').replace('-', ' ').title()
        return (
            market_data.get('question') or
            market_data.get('title') or
            slug
        )

    def parse_end_time(raw_value):
        if not raw_value:
            return None
        try:
            # ISO strings sometimes end with Z which datetime needs as +00:00
            if isinstance(raw_value, str):
                value = raw_value.replace('Z', '+00:00')
                end_dt = datetime.fromisoformat(value)
            else:
                end_dt = datetime.fromtimestamp(float(raw_value), tz=timezone.utc)
            if end_dt.tzinfo is None:
                end_dt = end_dt.replace(tzinfo=timezone.utc)
            return end_dt
        except Exception:
            return None

    try:
        try:
            limit = int(request.args.get('limit', 20))
        except (TypeError, ValueError):
            limit = 20

        now = datetime.now(timezone.utc)
        raw_markets = []
        try:
            raw_markets = client.gamma.get_markets(
                closed=False,
                limit=limit,
                order="volume",
                ascending=False
            )
        except Exception:
            raw_markets = []

        processed_markets = []
        for market in raw_markets:
            metrics = data_engine.calculate_market_metrics(market)
            title = normalize_title(market)
            slug = market.get('slug', '')
            category = market.get('category', 'N/A')
            volume = float(market.get('volume', 0) or 0)
            liquidity = float(market.get('liquidity', 0) or 0)
            end_time = parse_end_time(market.get('endDate'))
            hours_to_close = None
            if end_time:
                delta = (end_time - now).total_seconds() / 3600
                hours_to_close = round(delta, 2)

            outcome_prices = market.get('outcomePrices') or market.get('prices') or []
            implied_prob = None
            if isinstance(outcome_prices, list) and outcome_prices:
                try:
                    implied_prob = float(outcome_prices[0]) * 100
                except (TypeError, ValueError):
                    implied_prob = None

            sentiment_data = None
            condition_id = market.get('conditionId')
            if condition_id:
                try:
                    trades = client.data.get_trades(market=condition_id, limit=200)
                    if trades:
                        sentiment_data = data_engine.track_market_sentiment(trades, 12)
                except Exception:
                    sentiment_data = None

            processed_markets.append({
                'title': title,
                'slug': slug,
                'category': category,
                'volume': volume,
                'liquidity': liquidity,
                'endDate': market.get('endDate'),
                'hoursToClose': hours_to_close,
                'impliedProbability': implied_prob,
                'metrics': metrics.get('metrics', {}),
                'sentiment': sentiment_data,
            })

        # Build insights
        momentum_candidates = [
            m for m in processed_markets
            if m['sentiment']
            and m['sentiment'].get('score', 50) >= 55
            and m['sentiment'].get('confidence', 0) >= 10
        ]
        momentum_candidates.sort(
            key=lambda m: (
                m['sentiment']['score'],
                m['metrics'].get('activity_score', 0)
            ),
            reverse=True
        )

        value_candidates = sorted(
            processed_markets,
            key=lambda m: m['metrics'].get('vol_liq_ratio', 0),
            reverse=True
        )

        closing_candidates = [
            m for m in processed_markets
            if m['hoursToClose'] is not None and 0 < m['hoursToClose'] <= 72
        ]
        closing_candidates.sort(key=lambda m: m['hoursToClose'])

        whale_trades = []
        try:
            whale_trades = whale_tracker.get_recent_whales(limit=50)
        except Exception:
            whale_trades = []

        whale_buy_volume = sum(t.get('value', 0) for t in whale_trades if t.get('side') == 'BUY')
        whale_sell_volume = sum(t.get('value', 0) for t in whale_trades if t.get('side') == 'SELL')
        whale_flow = {}
        latest_whale = None

        for trade in whale_trades:
            market_title = trade.get('market', 'Unknown Market')
            flow = whale_flow.setdefault(market_title, {'buy': 0, 'sell': 0, 'slug': trade.get('marketSlug', '')})
            side = trade.get('side')
            value = trade.get('value', 0)
            if side == 'BUY':
                flow['buy'] += value
            elif side == 'SELL':
                flow['sell'] += value

            if (not latest_whale) or trade.get('timestamp', 0) > latest_whale.get('timestamp', 0):
                latest_whale = trade

        whale_leaderboard = sorted(
            (
                {
                    'market': market,
                    'slug': data['slug'],
                    'buyVolume': data['buy'],
                    'sellVolume': data['sell'],
                }
                for market, data in whale_flow.items()
            ),
            key=lambda item: item['buyVolume'] + item['sellVolume'],
            reverse=True
        )[:3]

        action_cards = []

        if momentum_candidates:
            top_momentum = momentum_candidates[0]
            action_cards.append({
                'type': 'momentum',
                'title': 'Bullish Momentum',
                'market': top_momentum['title'],
                'slug': top_momentum['slug'],
                'category': top_momentum['category'],
                'sentiment': top_momentum['sentiment'],
                'hint': 'Buyers have dominated trade flow over the last 12 hours. Review the order book before entering.',
                'dataPoints': [
                    {'label': 'Buy Flow', 'value': top_momentum['sentiment']['score'], 'format': 'percent'},
                    {'label': 'Liquidity', 'value': top_momentum['liquidity'], 'format': 'currency'},
                    {'label': 'Hours To Close', 'value': top_momentum['hoursToClose'], 'format': 'hours'},
                ]
            })

        if closing_candidates:
            urgent = closing_candidates[0]
            action_cards.append({
                'type': 'closing',
                'title': 'Closing Window',
                'market': urgent['title'],
                'slug': urgent['slug'],
                'category': urgent['category'],
                'hint': 'Expiring soon with meaningful liquidity. Double-check news catalysts before making a move.',
                'dataPoints': [
                    {'label': 'Hours Remaining', 'value': urgent['hoursToClose'], 'format': 'hours'},
                    {'label': '24h Volume', 'value': urgent['volume'], 'format': 'currency'},
                    {'label': 'Liquidity', 'value': urgent['liquidity'], 'format': 'currency'},
                ]
            })

        if whale_trades and latest_whale:
            action_cards.append({
                'type': 'whale',
                'title': 'Whale In The Water',
                'market': latest_whale.get('market', 'Unknown Market'),
                'slug': latest_whale.get('marketSlug', ''),
                'category': latest_whale.get('outcome', ''),
                'hint': f"Latest whale {latest_whale.get('side', '').title()} worth ${latest_whale.get('value', 0):,.0f}. Study how this aligns with your bias.",
                'dataPoints': [
                    {'label': 'Buy Whale Flow', 'value': whale_buy_volume, 'format': 'currency'},
                    {'label': 'Sell Whale Flow', 'value': whale_sell_volume, 'format': 'currency'},
                    {
                        'label': 'Trader',
                        'value': latest_whale.get('trader', 'Unknown'),
                        'format': 'text'
                    },
                ]
            })

        closing_soon = [
            {
                'market': m['title'],
                'slug': m['slug'],
                'hoursToClose': m['hoursToClose'],
                'volume': m['volume'],
                'liquidity': m['liquidity'],
                'category': m['category'],
                'impliedProbability': m['impliedProbability'],
            }
            for m in closing_candidates[:4]
        ]

        market_highlights = [
            {
                'market': m['title'],
                'slug': m['slug'],
                'category': m['category'],
                'volume': m['volume'],
                'liquidity': m['liquidity'],
                'volLiquidityRatio': m['metrics'].get('vol_liq_ratio'),
                'popularity': m['metrics'].get('popularity'),
                'health': m['metrics'].get('health'),
                'sentiment': m['sentiment'],
            }
            for m in value_candidates[:6]
        ]

        return jsonify({
            'success': True,
            'generatedAt': now.isoformat(),
            'actionCards': action_cards,
            'closingSoon': closing_soon,
            'marketHighlights': market_highlights,
            'whaleLeaderboard': whale_leaderboard,
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


@app.route('/api/trader/stats/<wallet_address>')
def get_trader_stats(wallet_address):
    """API endpoint to get trader statistics."""
    try:
        days = int(request.args.get('days', 30))
        stats = trader_analytics.calculate_trader_stats(wallet_address, days)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/trader/markets/<wallet_address>')
def get_trader_markets(wallet_address):
    """API endpoint to get trader's market performance."""
    try:
        limit = int(request.args.get('limit', 10))
        markets = trader_analytics.get_trader_market_performance(wallet_address, limit)
        
        return jsonify({
            'success': True,
            'markets': markets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/market/sentiment/<condition_id>')
def get_market_sentiment(condition_id):
    """API endpoint to get market sentiment analysis."""
    try:
        hours = int(request.args.get('hours', 24))
        
        # Get recent trades for this market
        trades = client.data.get_trades(market=condition_id, limit=500)
        
        # Calculate sentiment
        sentiment = data_engine.track_market_sentiment(trades, hours)
        
        return jsonify({
            'success': True,
            'sentiment': sentiment
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/market/enhanced/<slug>')
def get_enhanced_market(slug):
    """API endpoint to get enhanced market data with calculations."""
    try:
        # Get base market data
        market = client.gamma.get_market_by_slug(slug)
        
        # Enhance with calculated metrics
        enhanced_market = data_engine.calculate_market_metrics(market)
        
        # Get recent trades for sentiment
        condition_id = market.get('conditionId')
        if condition_id:
            trades = client.data.get_trades(market=condition_id, limit=200)
            sentiment = data_engine.track_market_sentiment(trades, 24)
            enhanced_market['sentiment'] = sentiment
        
        return jsonify({
            'success': True,
            'market': enhanced_market
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/traders/top')
def get_top_traders():
    """API endpoint to get top traders from whale activity."""
    try:
        # Get whale trades and aggregate by trader
        whale_trades = whale_tracker.get_recent_whales(limit=100)
        
        # Aggregate by trader
        trader_stats = {}
        for trade in whale_trades:
            wallet = trade.get('wallet', 'Unknown')
            if wallet not in trader_stats:
                trader_stats[wallet] = {
                    'wallet': wallet,
                    'trader_name': trade.get('trader', 'Unknown'),
                    'total_volume': 0,
                    'trade_count': 0,
                    'markets': set(),
                    'profile_image': trade.get('traderProfileImage', ''),
                }
            
            trader_stats[wallet]['total_volume'] += trade.get('value', 0)
            trader_stats[wallet]['trade_count'] += 1
            trader_stats[wallet]['markets'].add(trade.get('market', ''))
        
        # Convert to list and format
        traders = []
        for wallet, stats in trader_stats.items():
            traders.append({
                'wallet': stats['wallet'],
                'trader_name': stats['trader_name'],
                'total_volume': stats['total_volume'],
                'trade_count': stats['trade_count'],
                'unique_markets': len(stats['markets']),
                'profile_image': stats['profile_image'],
            })
        
        # Sort by volume
        traders.sort(key=lambda x: x['total_volume'], reverse=True)
        
        return jsonify({
            'success': True,
            'traders': traders[:20]
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

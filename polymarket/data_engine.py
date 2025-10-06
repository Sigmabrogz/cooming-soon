"""
Data Calculation Engine
-----------------------
Robust engine for calculating statistics, tracking data,
and maintaining historical records.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os


class DataEngine:
    """
    Centralized data calculation and caching engine.
    Handles all statistical calculations and data aggregation.
    """
    
    def __init__(self, cache_dir: str = './data_cache'):
        """
        Initialize data engine.
        
        Args:
            cache_dir: Directory for caching data
        """
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.market_cache = {}
        self.trader_cache = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def calculate_market_metrics(self, market_data: Dict) -> Dict:
        """
        Calculate comprehensive metrics for a market.
        
        Args:
            market_data: Raw market data
            
        Returns:
            Enhanced market data with calculated metrics
        """
        volume = float(market_data.get('volume', 0) or 0)
        liquidity = float(market_data.get('liquidity', 0) or 0)
        
        # Calculate volume to liquidity ratio
        vol_liq_ratio = volume / liquidity if liquidity > 0 else 0
        
        # Calculate trading activity score (0-100)
        activity_score = min(100, (volume / 100000) * 50 + (liquidity / 50000) * 50)
        
        # Determine market health
        if liquidity < 1000:
            health = 'Low Liquidity'
            health_score = 30
        elif liquidity < 10000:
            health = 'Moderate'
            health_score = 60
        else:
            health = 'Healthy'
            health_score = 90
        
        # Calculate popularity tier
        if volume >= 1000000:
            popularity = 'Viral 🔥'
        elif volume >= 100000:
            popularity = 'Trending 📈'
        elif volume >= 10000:
            popularity = 'Popular ⭐'
        elif volume >= 1000:
            popularity = 'Active 💫'
        else:
            popularity = 'Emerging 🌱'
        
        return {
            **market_data,
            'metrics': {
                'volume': volume,
                'liquidity': liquidity,
                'vol_liq_ratio': vol_liq_ratio,
                'activity_score': activity_score,
                'health': health,
                'health_score': health_score,
                'popularity': popularity,
            }
        }
    
    def aggregate_trader_data(self, trades: List[Dict]) -> Dict:
        """
        Aggregate and analyze trader activity data.
        
        Args:
            trades: List of trade records
            
        Returns:
            Aggregated trader statistics
        """
        if not trades:
            return self._empty_trader_data()
        
        # Initialize counters
        total_volume = 0
        buy_volume = 0
        sell_volume = 0
        markets = set()
        outcomes = defaultdict(int)
        hourly_activity = defaultdict(int)
        daily_volume = defaultdict(float)
        
        # Process each trade
        for trade in trades:
            size = float(trade.get('size', 0))
            price = float(trade.get('price', 0))
            value = size * price
            
            total_volume += value
            
            side = trade.get('side', '').upper()
            if side == 'BUY':
                buy_volume += value
            else:
                sell_volume += value
            
            # Track markets
            market_id = trade.get('conditionId', '')
            if market_id:
                markets.add(market_id)
            
            # Track outcomes
            outcome = trade.get('outcome', 'Unknown')
            outcomes[outcome] += 1
            
            # Track temporal patterns
            timestamp = trade.get('timestamp', 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                hourly_activity[dt.hour] += 1
                daily_volume[dt.date()] += value
        
        # Calculate statistics
        total_trades = len(trades)
        avg_trade_size = total_volume / total_trades
        
        buy_percentage = (buy_volume / total_volume * 100) if total_volume > 0 else 0
        sell_percentage = (sell_volume / total_volume * 100) if total_volume > 0 else 0
        
        # Find most active hour
        most_active_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0
        
        # Calculate daily average
        avg_daily_volume = sum(daily_volume.values()) / len(daily_volume) if daily_volume else 0
        
        # Find favorite outcome
        favorite_outcome = max(outcomes.items(), key=lambda x: x[1])[0] if outcomes else 'Unknown'
        
        return {
            'total_trades': total_trades,
            'total_volume': total_volume,
            'avg_trade_size': avg_trade_size,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'buy_percentage': buy_percentage,
            'sell_percentage': sell_percentage,
            'unique_markets': len(markets),
            'most_active_hour': most_active_hour,
            'avg_daily_volume': avg_daily_volume,
            'favorite_outcome': favorite_outcome,
            'outcome_distribution': dict(outcomes),
        }
    
    def _empty_trader_data(self) -> Dict:
        """Return empty trader data structure."""
        return {
            'total_trades': 0,
            'total_volume': 0,
            'avg_trade_size': 0,
            'buy_volume': 0,
            'sell_volume': 0,
            'unique_markets': 0,
        }
    
    def calculate_win_probability(
        self,
        historical_data: List[Dict],
        current_position: Dict
    ) -> float:
        """
        Calculate estimated win probability based on historical data.
        
        Args:
            historical_data: Historical trade/position data
            current_position: Current position details
            
        Returns:
            Estimated win probability (0-100)
        """
        if not historical_data:
            return 50.0  # No data = 50/50
        
        # Count wins and losses in similar scenarios
        wins = sum(1 for d in historical_data if float(d.get('cashPnl', 0)) > 0)
        total = len(historical_data)
        
        win_rate = (wins / total * 100) if total > 0 else 50.0
        
        # Adjust based on current market conditions
        # This is a simplified version - in production you'd use more sophisticated models
        
        return round(win_rate, 2)
    
    def track_market_sentiment(
        self,
        trades: List[Dict],
        time_window_hours: int = 24
    ) -> Dict:
        """
        Calculate market sentiment based on recent trading activity.
        
        Args:
            trades: List of trades
            time_window_hours: Time window for sentiment analysis
            
        Returns:
            Sentiment analysis data
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        recent_trades = [
            t for t in trades
            if t.get('timestamp', 0) >= cutoff_timestamp
        ]
        
        if not recent_trades:
            return {
                'sentiment': 'Neutral',
                'score': 50,
                'confidence': 0,
            }
        
        # Calculate buy vs sell pressure
        buy_volume = sum(
            float(t.get('size', 0)) * float(t.get('price', 0))
            for t in recent_trades
            if t.get('side', '').upper() == 'BUY'
        )
        
        sell_volume = sum(
            float(t.get('size', 0)) * float(t.get('price', 0))
            for t in recent_trades
            if t.get('side', '').upper() == 'SELL'
        )
        
        total_volume = buy_volume + sell_volume
        
        if total_volume == 0:
            return {
                'sentiment': 'Neutral',
                'score': 50,
                'confidence': 0,
            }
        
        # Calculate sentiment score (0-100, 50 is neutral)
        buy_ratio = buy_volume / total_volume
        sentiment_score = buy_ratio * 100
        
        # Determine sentiment label
        if sentiment_score >= 65:
            sentiment = 'Bullish 🚀'
        elif sentiment_score >= 55:
            sentiment = 'Slightly Bullish 📈'
        elif sentiment_score >= 45:
            sentiment = 'Neutral ➡️'
        elif sentiment_score >= 35:
            sentiment = 'Slightly Bearish 📉'
        else:
            sentiment = 'Bearish 🔻'
        
        # Calculate confidence based on sample size
        confidence = min(100, (len(recent_trades) / 50) * 100)
        
        return {
            'sentiment': sentiment,
            'score': round(sentiment_score, 2),
            'confidence': round(confidence, 2),
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'trade_count': len(recent_trades),
            'time_window_hours': time_window_hours,
        }
    
    def calculate_risk_metrics(self, position: Dict) -> Dict:
        """
        Calculate risk metrics for a position.
        
        Args:
            position: Position data
            
        Returns:
            Risk metrics
        """
        initial_value = float(position.get('initialValue', 0))
        current_value = float(position.get('currentValue', 0))
        pnl = float(position.get('cashPnl', 0))
        
        # Calculate risk metrics
        if initial_value > 0:
            roi = (pnl / initial_value) * 100
            value_at_risk = initial_value  # Maximum potential loss
            risk_reward_ratio = abs(pnl / initial_value) if pnl != 0 else 0
        else:
            roi = 0
            value_at_risk = 0
            risk_reward_ratio = 0
        
        # Determine risk level
        if abs(roi) < 10:
            risk_level = 'Low 🟢'
        elif abs(roi) < 25:
            risk_level = 'Moderate 🟡'
        else:
            risk_level = 'High 🔴'
        
        return {
            'roi_percentage': round(roi, 2),
            'value_at_risk': value_at_risk,
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'risk_level': risk_level,
            'potential_upside': max(0, current_value - initial_value),
            'potential_downside': initial_value,
        }
    
    def cache_data(self, key: str, data: Dict, ttl_seconds: int = 300):
        """
        Cache data in memory with TTL.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time to live in seconds
        """
        self.memory_cache[key] = {
            'data': data,
            'expires_at': int(time.time()) + ttl_seconds,
        }
    
    def get_cached_data(self, key: str) -> Optional[Dict]:
        """
        Retrieve cached data if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if expired/not found
        """
        if key not in self.memory_cache:
            return None
        
        cache_entry = self.memory_cache[key]
        
        if cache_entry['expires_at'] < int(time.time()):
            # Expired
            del self.memory_cache[key]
            return None
        
        return cache_entry['data']
    
    def save_to_disk(self, filename: str, data: Dict):
        """
        Save data to disk for persistence.
        
        Args:
            filename: Filename to save to
            data: Data to save
        """
        filepath = os.path.join(self.cache_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_disk(self, filename: str) -> Optional[Dict]:
        """
        Load data from disk.
        
        Args:
            filename: Filename to load from
            
        Returns:
            Loaded data or None if not found
        """
        filepath = os.path.join(self.cache_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None


import time


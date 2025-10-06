"""
Trader Analytics Engine
-----------------------
Advanced analytics system to track trader performance, win rates,
historical matches, and provide insights for copy trading.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
from collections import defaultdict


class TraderAnalytics:
    """Comprehensive trader analytics and performance tracking."""
    
    def __init__(self, data_api_client):
        """
        Initialize trader analytics engine.
        
        Args:
            data_api_client: DataAPIClient instance for fetching trade data
        """
        self.data_api = data_api_client
        self.trader_cache = {}
        self.performance_cache = {}
        
    def calculate_trader_stats(
        self,
        wallet_address: str,
        days: int = 30
    ) -> Dict:
        """
        Calculate comprehensive statistics for a trader.
        
        Args:
            wallet_address: Trader's proxy wallet address
            days: Number of days to analyze (default: 30)
            
        Returns:
            Dictionary with comprehensive trader statistics
        """
        # Calculate time range
        to_timestamp = int(datetime.now().timestamp())
        from_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Fetch trader data
        trades = self.data_api.get_trades(
            user=wallet_address,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            limit=1000
        )
        
        positions = self.data_api.get_positions(
            user=wallet_address,
            limit=1000
        )
        
        # Calculate statistics
        total_trades = len(trades)
        
        if total_trades == 0:
            return self._empty_stats(wallet_address)
        
        # Trade volume calculations
        total_volume = sum(
            float(trade.get('size', 0)) * float(trade.get('price', 0))
            for trade in trades
        )
        
        avg_trade_size = total_volume / total_trades if total_trades > 0 else 0
        
        # Position analysis
        total_positions = len(positions)
        open_positions = [p for p in positions if float(p.get('size', 0)) > 0]
        closed_positions = [p for p in positions if p.get('closed', False)]
        
        # Win/Loss calculations
        wins = 0
        losses = 0
        total_pnl = 0
        
        for position in positions:
            pnl = float(position.get('cashPnl', 0))
            total_pnl += pnl
            
            if pnl > 0:
                wins += 1
            elif pnl < 0:
                losses += 1
        
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        # ROI calculation
        total_invested = sum(
            float(p.get('initialValue', 0))
            for p in positions
        )
        
        roi = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        # Market diversity
        unique_markets = len(set(
            trade.get('conditionId', '')
            for trade in trades
        ))
        
        # Trading frequency
        if trades:
            first_trade_time = min(trade.get('timestamp', 0) for trade in trades)
            last_trade_time = max(trade.get('timestamp', 0) for trade in trades)
            active_days = (last_trade_time - first_trade_time) / 86400  # Convert to days
            trades_per_day = total_trades / active_days if active_days > 0 else 0
        else:
            trades_per_day = 0
        
        # Profit consistency
        position_pnls = [float(p.get('cashPnl', 0)) for p in positions if p.get('cashPnl')]
        pnl_std_dev = statistics.stdev(position_pnls) if len(position_pnls) > 1 else 0
        
        # Best and worst trades
        best_trade = max(position_pnls) if position_pnls else 0
        worst_trade = min(position_pnls) if position_pnls else 0
        
        # Average holding time
        holding_times = []
        for position in closed_positions:
            # This is an estimation - actual holding time would need trade timestamps
            holding_times.append(1)  # Placeholder
        
        avg_holding_time = statistics.mean(holding_times) if holding_times else 0
        
        return {
            'wallet_address': wallet_address,
            'analysis_period_days': days,
            'total_trades': total_trades,
            'total_volume': total_volume,
            'avg_trade_size': avg_trade_size,
            'total_positions': total_positions,
            'open_positions': len(open_positions),
            'closed_positions': len(closed_positions),
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'roi_percentage': roi,
            'unique_markets': unique_markets,
            'trades_per_day': trades_per_day,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'pnl_volatility': pnl_std_dev,
            'avg_holding_time_days': avg_holding_time,
            'risk_score': self._calculate_risk_score(pnl_std_dev, win_rate, roi),
            'trader_tier': self._calculate_trader_tier(total_volume, win_rate, roi),
        }
    
    def _empty_stats(self, wallet_address: str) -> Dict:
        """Return empty statistics for traders with no activity."""
        return {
            'wallet_address': wallet_address,
            'total_trades': 0,
            'total_volume': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'roi_percentage': 0,
            'trader_tier': 'Beginner',
            'risk_score': 0,
        }
    
    def _calculate_risk_score(
        self,
        pnl_volatility: float,
        win_rate: float,
        roi: float
    ) -> float:
        """
        Calculate a risk score (0-100, higher = riskier).
        
        Args:
            pnl_volatility: Standard deviation of P&L
            win_rate: Win rate percentage
            roi: Return on investment percentage
            
        Returns:
            Risk score between 0-100
        """
        # Normalize volatility (assuming max reasonable volatility of 10000)
        volatility_score = min(pnl_volatility / 100, 100)
        
        # Lower win rate = higher risk
        win_rate_risk = 100 - win_rate
        
        # Negative ROI = higher risk
        roi_risk = max(0, -roi)
        
        # Combine factors
        risk_score = (volatility_score * 0.4 + win_rate_risk * 0.4 + min(roi_risk, 100) * 0.2)
        
        return round(risk_score, 2)
    
    def _calculate_trader_tier(
        self,
        total_volume: float,
        win_rate: float,
        roi: float
    ) -> str:
        """
        Determine trader tier based on performance.
        
        Args:
            total_volume: Total trading volume
            win_rate: Win rate percentage
            roi: Return on investment percentage
            
        Returns:
            Trader tier: Whale, Expert, Advanced, Intermediate, Beginner
        """
        score = 0
        
        # Volume scoring
        if total_volume >= 1000000:
            score += 40
        elif total_volume >= 100000:
            score += 30
        elif total_volume >= 10000:
            score += 20
        elif total_volume >= 1000:
            score += 10
        
        # Win rate scoring
        if win_rate >= 70:
            score += 30
        elif win_rate >= 60:
            score += 20
        elif win_rate >= 50:
            score += 10
        
        # ROI scoring
        if roi >= 50:
            score += 30
        elif roi >= 25:
            score += 20
        elif roi >= 10:
            score += 10
        elif roi >= 0:
            score += 5
        
        # Tier assignment
        if score >= 80:
            return 'Whale 🐋'
        elif score >= 60:
            return 'Expert 💎'
        elif score >= 40:
            return 'Advanced 📈'
        elif score >= 20:
            return 'Intermediate 📊'
        else:
            return 'Beginner 🌱'
    
    def get_trader_market_performance(
        self,
        wallet_address: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get trader's performance breakdown by market.
        
        Args:
            wallet_address: Trader's wallet address
            limit: Number of markets to return
            
        Returns:
            List of market performance dictionaries
        """
        positions = self.data_api.get_positions(
            user=wallet_address,
            limit=500
        )
        
        # Group by market
        market_stats = defaultdict(lambda: {
            'trades': 0,
            'total_pnl': 0,
            'wins': 0,
            'losses': 0,
            'volume': 0,
            'market_title': '',
            'market_slug': '',
        })
        
        for position in positions:
            market_id = position.get('conditionId', '')
            pnl = float(position.get('cashPnl', 0))
            
            market_stats[market_id]['trades'] += 1
            market_stats[market_id]['total_pnl'] += pnl
            market_stats[market_id]['volume'] += float(position.get('initialValue', 0))
            
            if pnl > 0:
                market_stats[market_id]['wins'] += 1
            elif pnl < 0:
                market_stats[market_id]['losses'] += 1
            
            # Get market metadata
            event = position.get('event', {})
            market_stats[market_id]['market_title'] = event.get('title', 'Unknown Market')
            market_stats[market_id]['market_slug'] = event.get('slug', '')
        
        # Calculate win rates and sort by performance
        results = []
        for market_id, stats in market_stats.items():
            total_decided = stats['wins'] + stats['losses']
            win_rate = (stats['wins'] / total_decided * 100) if total_decided > 0 else 0
            
            results.append({
                'market_id': market_id,
                'market_title': stats['market_title'],
                'market_slug': stats['market_slug'],
                'trades': stats['trades'],
                'total_pnl': stats['total_pnl'],
                'wins': stats['wins'],
                'losses': stats['losses'],
                'win_rate': win_rate,
                'volume': stats['volume'],
            })
        
        # Sort by total P&L
        results.sort(key=lambda x: x['total_pnl'], reverse=True)
        
        return results[:limit]
    
    def get_top_traders(
        self,
        limit: int = 20,
        days: int = 30,
        min_volume: float = 1000
    ) -> List[Dict]:
        """
        Get leaderboard of top traders.
        
        Args:
            limit: Number of traders to return
            days: Analysis period in days
            min_volume: Minimum volume to be included
            
        Returns:
            List of top trader statistics
        """
        # This is a simplified version - in production, you'd want to:
        # 1. Maintain a database of known traders
        # 2. Periodically update their statistics
        # 3. Cache results for performance
        
        # For now, we'll return placeholder structure
        # You would populate this by tracking whale trades and building a database
        
        return []
    
    def compare_traders(
        self,
        wallet_addresses: List[str],
        days: int = 30
    ) -> Dict:
        """
        Compare multiple traders side by side.
        
        Args:
            wallet_addresses: List of wallet addresses to compare
            days: Analysis period in days
            
        Returns:
            Comparison dictionary with all trader stats
        """
        comparison = {
            'traders': [],
            'comparison_period_days': days,
        }
        
        for wallet in wallet_addresses:
            stats = self.calculate_trader_stats(wallet, days)
            comparison['traders'].append(stats)
        
        return comparison


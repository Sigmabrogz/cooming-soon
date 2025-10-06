"""
Copy Trading System
-------------------
Enable users to follow and automatically copy trades from successful traders.
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
import time
import threading


class CopyTrading:
    """Automated copy trading system for following successful traders."""
    
    def __init__(self, clob_client, data_api_client):
        """
        Initialize copy trading system.
        
        Args:
            clob_client: CLOBClient instance for placing orders
            data_api_client: DataAPIClient instance for monitoring trades
        """
        self.clob = clob_client
        self.data_api = data_api_client
        self.following = {}  # wallet_address -> follow_settings
        self.active_monitors = {}  # wallet_address -> thread
        self.last_checked_trades = {}  # wallet_address -> timestamp
        
    def follow_trader(
        self,
        trader_wallet: str,
        copy_settings: Optional[Dict] = None
    ) -> Dict:
        """
        Start following a trader and copy their trades.
        
        Args:
            trader_wallet: Wallet address of trader to follow
            copy_settings: Dictionary with copy trading settings:
                - max_position_size: Maximum size per position (default: 100)
                - copy_percentage: Percentage of their trade to copy (default: 10)
                - max_total_exposure: Maximum total exposure across all positions
                - markets_to_copy: List of market slugs to copy (None = all)
                - markets_to_exclude: List of market slugs to exclude
                - min_trader_confidence: Minimum position size to copy (filters small trades)
                - auto_exit: Whether to copy exit trades (default: True)
                
        Returns:
            Follow confirmation with settings
        """
        default_settings = {
            'max_position_size': 100,
            'copy_percentage': 10,
            'max_total_exposure': 1000,
            'markets_to_copy': None,
            'markets_to_exclude': [],
            'min_trader_confidence': 10,
            'auto_exit': True,
            'enabled': True,
        }
        
        # Merge with user settings
        settings = {**default_settings, **(copy_settings or {})}
        
        # Store follow settings
        self.following[trader_wallet] = {
            'trader_wallet': trader_wallet,
            'settings': settings,
            'started_at': int(time.time()),
            'total_copied_trades': 0,
            'total_volume_copied': 0,
        }
        
        # Initialize last checked timestamp
        self.last_checked_trades[trader_wallet] = int(time.time())
        
        return {
            'success': True,
            'trader_wallet': trader_wallet,
            'settings': settings,
            'message': f'Now following {trader_wallet}'
        }
    
    def unfollow_trader(self, trader_wallet: str) -> Dict:
        """
        Stop following a trader.
        
        Args:
            trader_wallet: Wallet address to unfollow
            
        Returns:
            Unfollow confirmation
        """
        if trader_wallet in self.following:
            follow_data = self.following.pop(trader_wallet)
            self.last_checked_trades.pop(trader_wallet, None)
            
            return {
                'success': True,
                'trader_wallet': trader_wallet,
                'total_copied_trades': follow_data['total_copied_trades'],
                'total_volume_copied': follow_data['total_volume_copied'],
                'message': f'Unfollowed {trader_wallet}'
            }
        else:
            return {
                'success': False,
                'message': f'Not following {trader_wallet}'
            }
    
    def get_following_list(self) -> List[Dict]:
        """
        Get list of all traders being followed.
        
        Returns:
            List of followed traders with their settings and stats
        """
        return list(self.following.values())
    
    def check_for_new_trades(self, trader_wallet: str) -> List[Dict]:
        """
        Check for new trades from a followed trader.
        
        Args:
            trader_wallet: Wallet address to check
            
        Returns:
            List of new trades to potentially copy
        """
        if trader_wallet not in self.following:
            return []
        
        last_checked = self.last_checked_trades.get(trader_wallet, int(time.time()) - 3600)
        
        # Fetch recent trades
        trades = self.data_api.get_trades(
            user=trader_wallet,
            from_timestamp=last_checked,
            limit=50
        )
        
        # Update last checked timestamp
        self.last_checked_trades[trader_wallet] = int(time.time())
        
        # Filter for new trades
        new_trades = [
            trade for trade in trades
            if trade.get('timestamp', 0) > last_checked
        ]
        
        return new_trades
    
    def should_copy_trade(self, trade: Dict, settings: Dict) -> bool:
        """
        Determine if a trade should be copied based on settings.
        
        Args:
            trade: Trade data
            settings: Copy trading settings
            
        Returns:
            True if trade should be copied
        """
        # Check if copying is enabled
        if not settings.get('enabled', True):
            return False
        
        # Check minimum trader confidence (position size)
        trade_size = float(trade.get('size', 0)) * float(trade.get('price', 0))
        if trade_size < settings.get('min_trader_confidence', 0):
            return False
        
        # Check market filters
        market_slug = trade.get('market', {}).get('slug', '')
        
        markets_to_copy = settings.get('markets_to_copy')
        if markets_to_copy and market_slug not in markets_to_copy:
            return False
        
        markets_to_exclude = settings.get('markets_to_exclude', [])
        if market_slug in markets_to_exclude:
            return False
        
        return True
    
    def calculate_copy_size(self, trade: Dict, settings: Dict) -> float:
        """
        Calculate the size to copy based on settings.
        
        Args:
            trade: Original trade data
            settings: Copy trading settings
            
        Returns:
            Size to copy
        """
        original_size = float(trade.get('size', 0))
        copy_percentage = settings.get('copy_percentage', 10) / 100
        
        # Calculate copy size
        copy_size = original_size * copy_percentage
        
        # Apply maximum position size limit
        max_size = settings.get('max_position_size', 100)
        copy_size = min(copy_size, max_size)
        
        return copy_size
    
    def copy_trade(
        self,
        trader_wallet: str,
        trade: Dict
    ) -> Optional[Dict]:
        """
        Copy a trade from a followed trader.
        
        Args:
            trader_wallet: Wallet of trader being copied
            trade: Trade data to copy
            
        Returns:
            Order response or None if not copied
        """
        if trader_wallet not in self.following:
            return None
        
        follow_data = self.following[trader_wallet]
        settings = follow_data['settings']
        
        # Check if we should copy this trade
        if not self.should_copy_trade(trade, settings):
            return None
        
        # Calculate copy size
        copy_size = self.calculate_copy_size(trade, settings)
        
        if copy_size <= 0:
            return None
        
        # Get trade details
        token_id = trade.get('asset', '')
        price = float(trade.get('price', 0))
        side = trade.get('side', 'BUY').upper()
        
        try:
            # Place the copy order
            order_response = self.clob.place_order(
                token_id=token_id,
                price=price,
                size=copy_size,
                side=side
            )
            
            # Update statistics
            follow_data['total_copied_trades'] += 1
            follow_data['total_volume_copied'] += copy_size * price
            
            return {
                'success': True,
                'order': order_response,
                'copied_from': trader_wallet,
                'original_trade': trade,
                'copy_size': copy_size,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'copied_from': trader_wallet,
                'original_trade': trade,
            }
    
    def monitor_trader(
        self,
        trader_wallet: str,
        check_interval: int = 30,
        callback: Optional[Callable] = None
    ):
        """
        Continuously monitor a trader and copy their trades.
        
        Args:
            trader_wallet: Wallet to monitor
            check_interval: Seconds between checks
            callback: Optional callback function for notifications
        """
        print(f"📊 Monitoring {trader_wallet} for copy trading...")
        
        while trader_wallet in self.following:
            try:
                # Check for new trades
                new_trades = self.check_for_new_trades(trader_wallet)
                
                for trade in new_trades:
                    # Attempt to copy the trade
                    result = self.copy_trade(trader_wallet, trade)
                    
                    if result and result.get('success'):
                        print(f"✅ Copied trade from {trader_wallet[:8]}...")
                        print(f"   Market: {trade.get('market', {}).get('title', 'Unknown')}")
                        print(f"   Side: {trade.get('side')}, Size: {result['copy_size']}")
                        
                        if callback:
                            callback(result)
                    elif result:
                        print(f"❌ Failed to copy trade: {result.get('error', 'Unknown error')}")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"⚠️  Error monitoring {trader_wallet}: {e}")
                time.sleep(check_interval)
    
    def start_monitoring(
        self,
        trader_wallet: str,
        check_interval: int = 30,
        callback: Optional[Callable] = None
    ):
        """
        Start monitoring a trader in a background thread.
        
        Args:
            trader_wallet: Wallet to monitor
            check_interval: Seconds between checks
            callback: Optional callback for notifications
        """
        if trader_wallet not in self.following:
            raise ValueError(f"Not following {trader_wallet}")
        
        if trader_wallet in self.active_monitors:
            print(f"Already monitoring {trader_wallet}")
            return
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self.monitor_trader,
            args=(trader_wallet, check_interval, callback),
            daemon=True
        )
        monitor_thread.start()
        
        self.active_monitors[trader_wallet] = monitor_thread
    
    def stop_monitoring(self, trader_wallet: str):
        """
        Stop monitoring a trader.
        
        Args:
            trader_wallet: Wallet to stop monitoring
        """
        if trader_wallet in self.active_monitors:
            # Unfollow will stop the monitor thread
            self.unfollow_trader(trader_wallet)
            self.active_monitors.pop(trader_wallet, None)
            print(f"Stopped monitoring {trader_wallet}")
    
    def get_copy_trade_performance(self, trader_wallet: str) -> Dict:
        """
        Get performance statistics for copy trading a specific trader.
        
        Args:
            trader_wallet: Wallet address
            
        Returns:
            Performance statistics
        """
        if trader_wallet not in self.following:
            return {
                'error': f'Not following {trader_wallet}'
            }
        
        follow_data = self.following[trader_wallet]
        
        # Calculate duration
        duration_seconds = int(time.time()) - follow_data['started_at']
        duration_days = duration_seconds / 86400
        
        return {
            'trader_wallet': trader_wallet,
            'following_since': datetime.fromtimestamp(follow_data['started_at']).strftime('%Y-%m-%d %H:%M:%S'),
            'duration_days': round(duration_days, 2),
            'total_copied_trades': follow_data['total_copied_trades'],
            'total_volume_copied': follow_data['total_volume_copied'],
            'avg_volume_per_trade': (
                follow_data['total_volume_copied'] / follow_data['total_copied_trades']
                if follow_data['total_copied_trades'] > 0 else 0
            ),
            'trades_per_day': (
                follow_data['total_copied_trades'] / duration_days
                if duration_days > 0 else 0
            ),
            'settings': follow_data['settings'],
        }


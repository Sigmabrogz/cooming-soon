"""
Whale Activity Tracker
----------------------
Monitors large trades on Polymarket and triggers alerts for unusual activity.
"""

import time
import requests
from datetime import datetime
from typing import List, Dict, Set
import json


class WhaleTracker:
    """Track and alert on large trades (whale activity)."""
    
    def __init__(self, min_trade_amount: float = 10000):
        """
        Initialize whale tracker.
        
        Args:
            min_trade_amount: Minimum trade value in USD to trigger alert (default: $10,000)
        """
        self.min_trade_amount = min_trade_amount
        self.base_url = "https://data-api.polymarket.com"
        self.seen_transactions: Set[str] = set()
        self.whale_trades: List[Dict] = []
        self.max_history = 100  # Keep last 100 whale trades
        
    def fetch_whale_trades(self) -> List[Dict]:
        """
        Fetch recent large trades from Polymarket.
        
        Returns:
            List of whale trade objects
        """
        try:
            params = {
                'filterType': 'CASH',
                'filterAmount': self.min_trade_amount,
                'limit': 50,  # Get last 50 large trades
            }
            
            response = requests.get(
                f"{self.base_url}/trades",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                trades = response.json()
                return trades if isinstance(trades, list) else []
            else:
                print(f"Error fetching trades: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching whale trades: {e}")
            return []
    
    def process_trade(self, trade: Dict) -> Dict:
        """
        Process and format a whale trade for display.
        
        Args:
            trade: Raw trade data from API
            
        Returns:
            Formatted trade information
        """
        # Calculate trade value
        size = float(trade.get('size', 0))
        price = float(trade.get('price', 0))
        value = size * price
        
        # Get market title - API returns it at root level as 'title'
        market_title = trade.get('title', 'Unknown Market')
        
        # Get market slug - API returns it at root level as 'slug' or 'eventSlug'
        market_slug = trade.get('slug') or trade.get('eventSlug', '')
        
        # Get trader info - API returns at root level
        wallet = trade.get('proxyWallet', 'Unknown')
        trader_name = (
            trade.get('name') or 
            trade.get('pseudonym') or
            f"{wallet[:6]}...{wallet[-4:]}" if wallet != 'Unknown' else 'Unknown'
        )
        
        # Get side and outcome - API returns at root level
        side = trade.get('side', '').upper()
        outcome = trade.get('outcome', 'Unknown')
        outcome_index = trade.get('outcomeIndex', 0)
        
        # Get icon URL if available
        icon_url = trade.get('icon', '')
        
        return {
            'transactionHash': trade.get('transactionHash', ''),
            'timestamp': trade.get('timestamp', 0),
            'market': market_title,
            'marketSlug': market_slug,
            'eventSlug': trade.get('eventSlug', ''),
            'side': side,
            'outcome': outcome,
            'outcomeIndex': outcome_index,
            'size': size,
            'price': price,
            'value': value,
            'trader': trader_name,
            'wallet': wallet,
            'conditionId': trade.get('conditionId', ''),
            'assetId': trade.get('asset', ''),
            'iconUrl': icon_url,
            'traderBio': trade.get('bio', ''),
            'traderProfileImage': trade.get('profileImage', ''),
        }
    
    def check_for_new_whales(self) -> List[Dict]:
        """
        Check for new whale trades and return only unseen ones.
        
        Returns:
            List of new whale trades
        """
        new_whales = []
        
        # Fetch latest trades
        trades = self.fetch_whale_trades()
        
        for trade in trades:
            tx_hash = trade.get('transactionHash', '')
            
            # Skip if we've already seen this transaction
            if tx_hash and tx_hash not in self.seen_transactions:
                processed_trade = self.process_trade(trade)
                new_whales.append(processed_trade)
                
                # Mark as seen
                self.seen_transactions.add(tx_hash)
                
                # Add to history
                self.whale_trades.insert(0, processed_trade)
                
                # Trim history if needed
                if len(self.whale_trades) > self.max_history:
                    self.whale_trades = self.whale_trades[:self.max_history]
        
        return new_whales
    
    def format_alert(self, trade: Dict) -> str:
        """
        Format a whale trade alert message.
        
        Args:
            trade: Processed trade data
            
        Returns:
            Formatted alert string
        """
        timestamp = datetime.fromtimestamp(trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        alert = f"""
🐋 WHALE ALERT! Unusual Bet Activity Detected

💰 Value: ${trade['value']:,.2f}
📊 Market: {trade['market']}
🎯 Side: {trade['side']} ({trade['outcome']})
👤 Trader: {trade['trader']}
📈 Size: {trade['size']:,.2f} shares @ ${trade['price']:.4f}
⏰ Time: {timestamp}
🔗 Transaction: {trade['transactionHash'][:10]}...
"""
        return alert
    
    def get_recent_whales(self, limit: int = 20) -> List[Dict]:
        """
        Get recent whale trades from history.
        
        Args:
            limit: Maximum number of trades to return
            
        Returns:
            List of recent whale trades
        """
        return self.whale_trades[:limit]
    
    def run_monitor(self, interval: int = 5, callback=None):
        """
        Run continuous monitoring loop.
        
        Args:
            interval: Seconds between checks
            callback: Optional function to call with new whale trades
        """
        print(f"\n🐋 Starting Whale Activity Monitor")
        print(f"💰 Tracking trades >= ${self.min_trade_amount:,.0f}")
        print(f"🔄 Checking every {interval} seconds")
        print("="*80 + "\n")
        
        try:
            while True:
                new_whales = self.check_for_new_whales()
                
                if new_whales:
                    for whale in new_whales:
                        alert = self.format_alert(whale)
                        print(alert)
                        
                        if callback:
                            callback(whale)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Whale monitor stopped")
        except Exception as e:
            print(f"\n❌ Error in monitor: {e}")


def main():
    """Run whale tracker as standalone script."""
    # Create tracker (default $10,000 minimum)
    tracker = WhaleTracker(min_trade_amount=10000)
    
    # Run continuous monitoring
    tracker.run_monitor(interval=5)


if __name__ == "__main__":
    main()

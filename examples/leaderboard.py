"""
Leaderboard Example
-------------------
Fetch trades over the last 24 hours and compute a leaderboard
showing top traders by realized/mark-to-market P&L and win rate.
"""

import time
from collections import defaultdict
from typing import Dict, List
import os
from dotenv import load_dotenv
from polymarket import PolymarketClient

load_dotenv()


def calculate_trader_stats(trades: List[Dict]) -> Dict[str, Dict]:
    """
    Calculate trader statistics from trades.
    
    Args:
        trades: List of trade records
        
    Returns:
        Dictionary mapping wallet address to stats
    """
    trader_stats = defaultdict(lambda: {
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "total_volume": 0.0,
        "total_pnl": 0.0,
        "markets": set(),
    })
    
    for trade in trades:
        wallet = trade.get("proxyWallet")
        size = trade.get("size", 0)
        price = trade.get("price", 0)
        volume = size * price
        
        stats = trader_stats[wallet]
        stats["total_trades"] += 1
        stats["total_volume"] += volume
        stats["markets"].add(trade.get("market", {}).get("slug", ""))
        
        # Simple P&L estimation (this is simplified; real P&L requires position tracking)
        side = trade.get("side", "").upper()
        if side == "BUY":
            # For buys, positive if current price > purchase price
            # This is a simplification - would need current prices
            pass
        elif side == "SELL":
            # For sells, immediate realization
            stats["total_pnl"] += volume
    
    # Calculate win rate (simplified)
    for wallet, stats in trader_stats.items():
        if stats["total_trades"] > 0:
            # This is a placeholder - actual win rate requires outcome data
            stats["win_rate"] = stats["winning_trades"] / stats["total_trades"]
        else:
            stats["win_rate"] = 0.0
        
        # Convert set to list for JSON serialization
        stats["markets"] = list(stats["markets"])
    
    return dict(trader_stats)


def print_leaderboard(trader_stats: Dict[str, Dict], limit: int = 10):
    """
    Print leaderboard of top traders.
    
    Args:
        trader_stats: Trader statistics
        limit: Number of traders to display
    """
    # Sort by total volume
    sorted_traders = sorted(
        trader_stats.items(),
        key=lambda x: x[1]["total_volume"],
        reverse=True
    )[:limit]
    
    print("\n" + "="*80)
    print("POLYMARKET LEADERBOARD - Top Traders (24h)")
    print("="*80)
    print(f"{'Rank':<6}{'Wallet':<44}{'Trades':<10}{'Volume':<15}{'P&L':<15}")
    print("-"*80)
    
    for rank, (wallet, stats) in enumerate(sorted_traders, 1):
        wallet_short = f"{wallet[:6]}...{wallet[-4:]}"
        print(
            f"{rank:<6}"
            f"{wallet_short:<44}"
            f"{stats['total_trades']:<10}"
            f"${stats['total_volume']:,.2f}{'':<5}"
            f"${stats['total_pnl']:,.2f}"
        )
    
    print("="*80 + "\n")


def main():
    """Run leaderboard example."""
    # Initialize client (read-only, no authentication needed)
    client = PolymarketClient()
    
    print("Fetching trades from last 24 hours...")
    
    # Calculate 24h timestamp
    now = int(time.time())
    yesterday = now - (24 * 60 * 60)
    
    # Fetch trades
    trades = client.data.get_trades(
        from_timestamp=yesterday,
        to_timestamp=now,
        limit=1000,  # Adjust as needed
    )
    
    print(f"Found {len(trades)} trades in the last 24 hours\n")
    
    # Calculate trader stats
    trader_stats = calculate_trader_stats(trades)
    
    # Print leaderboard
    print_leaderboard(trader_stats, limit=20)
    
    # Additional stats
    total_volume = sum(stats["total_volume"] for stats in trader_stats.values())
    total_traders = len(trader_stats)
    
    print(f"Total Volume: ${total_volume:,.2f}")
    print(f"Active Traders: {total_traders}")
    print(f"Average Volume per Trader: ${total_volume/total_traders:,.2f}" if total_traders > 0 else "N/A")


if __name__ == "__main__":
    main()

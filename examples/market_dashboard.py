"""
Market Dashboard Example
------------------------
Display active markets with real-time orderbook and price updates.
"""

import os
import time
from typing import Dict, Any
from dotenv import load_dotenv
from polymarket import PolymarketClient
from polymarket.websocket import CLOBMarketWebSocket

load_dotenv()


def print_market_info(market: Dict[str, Any]):
    """Print market information."""
    print("\n" + "="*100)
    print(f"Market: {market.get('title', 'Unknown')}")
    print("="*100)
    print(f"Slug: {market.get('slug', '')}")
    print(f"Condition ID: {market.get('conditionId', '')}")
    print(f"Status: {market.get('status', '')}")
    print(f"Liquidity: ${market.get('liquidity', 0):,.2f}")
    print(f"Volume: ${market.get('volume', 0):,.2f}")
    print(f"End Date: {market.get('endDate', 'N/A')}")
    print("="*100 + "\n")


def print_orderbook(book_data: Dict[str, Any]):
    """Print orderbook in a formatted table."""
    buys = book_data.get("buys", [])[:10]  # Top 10 bids
    sells = book_data.get("sells", [])[:10]  # Top 10 asks
    best_bid = book_data.get("bestBid")
    best_ask = book_data.get("bestAsk")
    
    print("\n" + "="*80)
    print("ORDER BOOK")
    print("="*80)
    
    if best_bid and best_ask:
        spread = best_ask - best_bid
        spread_pct = (spread / best_bid) * 100 if best_bid > 0 else 0
        print(f"Spread: ${spread:.4f} ({spread_pct:.2f}%)")
        print("-"*80)
    
    # Print header
    print(f"{'BIDS':<35}{'':10}{'ASKS':<35}")
    print(f"{'Price':<15}{'Size':<20}{'':10}{'Price':<15}{'Size':<20}")
    print("-"*80)
    
    # Print order book levels
    max_rows = max(len(buys), len(sells))
    for i in range(max_rows):
        bid_str = ""
        ask_str = ""
        
        if i < len(buys):
            bid_price, bid_size = buys[i]
            bid_str = f"${bid_price:<14.4f}{bid_size:<20.2f}"
        else:
            bid_str = " " * 35
        
        if i < len(sells):
            ask_price, ask_size = sells[i]
            ask_str = f"${ask_price:<14.4f}{ask_size:<20.2f}"
        else:
            ask_str = " " * 35
        
        print(f"{bid_str}{'':10}{ask_str}")
    
    print("="*80 + "\n")


def print_top_holders(holders: list, limit: int = 10):
    """Print top holders."""
    if not holders:
        print("No holder data available.\n")
        return
    
    print("\n" + "="*80)
    print(f"TOP HOLDERS (Top {limit})")
    print("="*80)
    print(f"{'Rank':<8}{'Wallet':<44}{'Balance':<20}")
    print("-"*80)
    
    for rank, holder in enumerate(holders[:limit], 1):
        wallet = holder.get("proxyWallet", "Unknown")
        wallet_short = f"{wallet[:6]}...{wallet[-4:]}"
        name = holder.get("name") or holder.get("pseudonym", "Anonymous")
        amount = holder.get("amount", 0)
        
        display_name = f"{wallet_short} ({name})" if name != "Anonymous" else wallet_short
        
        print(f"{rank:<8}{display_name:<44}{amount:<20,.2f}")
    
    print("="*80 + "\n")


def on_book_update(data):
    """Callback for orderbook updates."""
    print(f"\n📊 Orderbook updated at {time.strftime('%H:%M:%S')}")
    print_orderbook(data)


def on_price_change(data):
    """Callback for price changes."""
    price = data.get("price", 0)
    side = data.get("side", "")
    size_change = data.get("sizeChange", 0)
    
    direction = "📈" if side == "buy" else "📉"
    print(f"{direction} Price change: ${price:.4f} ({side.upper()}) - Size change: {size_change:+.2f}")


def on_last_trade(data):
    """Callback for last trade price."""
    price = data.get("price", 0)
    size = data.get("size", 0)
    side = data.get("side", "")
    timestamp = data.get("timestamp", 0)
    
    time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
    print(f"💰 Last trade: {side.upper()} {size:.2f} @ ${price:.4f} at {time_str}")


def main():
    """Run market dashboard example."""
    # Initialize client
    client = PolymarketClient()
    
    print("\n" + "="*100)
    print("POLYMARKET DASHBOARD")
    print("="*100)
    
    # Fetch active markets
    print("\nFetching active markets...")
    markets = client.gamma.get_markets(closed=False, limit=10, order="volume", ascending=False)
    
    if not markets:
        print("No active markets found.")
        return
    
    print(f"\nFound {len(markets)} active markets\n")
    
    # Display top markets
    print("Top Markets by Volume:")
    print("-" * 100)
    for i, market in enumerate(markets[:5], 1):
        print(f"{i}. {market.get('title', 'Unknown')}")
        print(f"   Volume: ${market.get('volume', 0):,.2f} | Liquidity: ${market.get('liquidity', 0):,.2f}")
        print(f"   Slug: {market.get('slug', '')}\n")
    
    # Select first market for detailed view
    selected_market = markets[0]
    market_slug = selected_market.get("slug", "")
    condition_id = selected_market.get("conditionId", "")
    
    print_market_info(selected_market)
    
    # Fetch holders
    print(f"Fetching top holders for {market_slug}...")
    try:
        holders_data = client.data.get_holders(market=condition_id, limit=20)
        holders = holders_data.get("holders", [])
        print_top_holders(holders, limit=10)
    except Exception as e:
        print(f"Could not fetch holders: {e}\n")
    
    # Optional: Start WebSocket for real-time orderbook updates
    use_websocket = input("\nStart real-time orderbook updates? (y/n): ").lower().strip()
    
    if use_websocket == 'y':
        print("\n" + "="*100)
        print(f"Starting real-time updates for: {selected_market.get('title', '')}")
        print("="*100)
        print("(Press Ctrl+C to stop)\n")
        
        ws = CLOBMarketWebSocket()
        ws.subscribe_market(
            asset_ids=[selected_market.get("token0Id"), selected_market.get("token1Id")],
            on_book=on_book_update,
            on_price_change=on_price_change,
            on_last_trade=on_last_trade,
        )
        
        try:
            ws.run(run_forever=True)
        except KeyboardInterrupt:
            print("\n\nStopping dashboard...")
            ws.close()
    else:
        print("\nDashboard complete. Run again to monitor other markets.")


if __name__ == "__main__":
    main()

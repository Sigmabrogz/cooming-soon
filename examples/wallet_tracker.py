"""
Wallet Tracker Example
----------------------
Track a specific wallet's positions and activity with real-time updates.
"""

import os
import time
from dotenv import load_dotenv
from polymarket import PolymarketClient
from polymarket.websocket import CLOBUserWebSocket

load_dotenv()


def print_positions(positions):
    """Print wallet positions in a formatted table."""
    if not positions:
        print("No open positions found.\n")
        return
    
    print("\n" + "="*100)
    print("OPEN POSITIONS")
    print("="*100)
    print(f"{'Market':<40}{'Size':<12}{'Avg Price':<12}{'Current':<12}{'P&L':<12}{'P&L %':<12}")
    print("-"*100)
    
    total_value = 0
    total_pnl = 0
    
    for pos in positions:
        market_name = pos.get("market", {}).get("title", "Unknown")[:38]
        size = pos.get("size", 0)
        avg_price = pos.get("avgPrice", 0)
        cur_price = pos.get("curPrice", 0)
        cash_pnl = pos.get("cashPnl", 0)
        percent_pnl = pos.get("percentPnl", 0)
        current_value = pos.get("currentValue", 0)
        
        total_value += current_value
        total_pnl += cash_pnl
        
        pnl_color = "+" if cash_pnl >= 0 else ""
        
        print(
            f"{market_name:<40}"
            f"{size:<12.2f}"
            f"${avg_price:<11.4f}"
            f"${cur_price:<11.4f}"
            f"{pnl_color}${cash_pnl:<11.2f}"
            f"{pnl_color}{percent_pnl:<11.2f}%"
        )
    
    print("-"*100)
    print(f"{'TOTAL':<40}{'':12}{'':12}${total_value:<11.2f}${total_pnl:<11.2f}")
    print("="*100 + "\n")


def print_recent_trades(trades, limit=10):
    """Print recent trades."""
    if not trades:
        print("No recent trades found.\n")
        return
    
    print("\n" + "="*100)
    print(f"RECENT TRADES (Last {limit})")
    print("="*100)
    print(f"{'Time':<20}{'Market':<40}{'Side':<8}{'Size':<12}{'Price':<12}")
    print("-"*100)
    
    for trade in trades[:limit]:
        timestamp = trade.get("timestamp", 0)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        market_name = trade.get("market", {}).get("title", "Unknown")[:38]
        side = trade.get("side", "").upper()
        size = trade.get("size", 0)
        price = trade.get("price", 0)
        
        print(
            f"{time_str:<20}"
            f"{market_name:<40}"
            f"{side:<8}"
            f"{size:<12.2f}"
            f"${price:<12.4f}"
        )
    
    print("="*100 + "\n")


def on_order_update(data):
    """Callback for order updates."""
    order_type = data.get("type", "")
    market = data.get("market", "")
    side = data.get("side", "")
    size = data.get("size", 0)
    price = data.get("price", 0)
    
    if order_type == "PLACEMENT":
        print(f"🔵 NEW ORDER: {side} {size} @ ${price} in {market}")
    elif order_type == "CANCELLATION":
        print(f"🔴 ORDER CANCELLED: {side} {size} @ ${price} in {market}")
    elif order_type == "UPDATE":
        size_matched = data.get("sizeMatched", 0)
        print(f"🟢 ORDER MATCHED: {size_matched}/{size} @ ${price} in {market}")


def on_trade_update(data):
    """Callback for trade updates."""
    market = data.get("market", "")
    side = data.get("side", "")
    size = data.get("size", 0)
    price = data.get("price", 0)
    
    print(f"✅ TRADE EXECUTED: {side} {size} @ ${price} in {market}")


def main():
    """Run wallet tracker example."""
    # Get wallet address from environment
    wallet_address = os.getenv("PROXY_WALLET_ADDRESS")
    
    if not wallet_address:
        print("Error: PROXY_WALLET_ADDRESS not set in .env file")
        return
    
    # Initialize client
    client = PolymarketClient()
    
    print(f"\nTracking wallet: {wallet_address}\n")
    print("="*100)
    
    # Fetch current positions
    print("Fetching current positions...")
    positions = client.data.get_positions(user=wallet_address, closed=False)
    print_positions(positions)
    
    # Fetch recent trades
    print("Fetching recent trades...")
    trades = client.data.get_trades(user=wallet_address, limit=20)
    print_recent_trades(trades, limit=10)
    
    # Get portfolio value
    portfolio = client.data.get_portfolio_value(user=wallet_address)
    print(f"Total Portfolio Value: ${portfolio.get('value', 0):,.2f}\n")
    
    # Optional: Start WebSocket for real-time updates
    api_key = os.getenv("POLY_API_KEY")
    secret = os.getenv("POLY_SECRET")
    passphrase = os.getenv("POLY_PASSPHRASE")
    
    if all([api_key, secret, passphrase]):
        print("\n" + "="*100)
        print("Starting real-time tracking... (Press Ctrl+C to stop)")
        print("="*100 + "\n")
        
        ws = CLOBUserWebSocket(api_key, secret, passphrase)
        ws.subscribe(
            markets=["all"],
            on_order=on_order_update,
            on_trade=on_trade_update,
        )
        
        try:
            ws.run(run_forever=True)
        except KeyboardInterrupt:
            print("\n\nStopping tracker...")
            ws.close()
    else:
        print("Note: Set API credentials in .env for real-time updates")


if __name__ == "__main__":
    main()

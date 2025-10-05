"""
WebSocket Streaming Example
---------------------------
Examples of real-time data streaming from Polymarket.
"""

import os
import time
from dotenv import load_dotenv
from polymarket.websocket import CLOBUserWebSocket, CLOBMarketWebSocket, RTDSWebSocket

load_dotenv()


def user_channel_example():
    """Example: Subscribe to user channel for order and trade updates."""
    api_key = os.getenv("POLY_API_KEY")
    secret = os.getenv("POLY_SECRET")
    passphrase = os.getenv("POLY_PASSPHRASE")
    
    if not all([api_key, secret, passphrase]):
        print("Error: API credentials not set. Run derive_api_key.py first.")
        return
    
    print("\n" + "="*80)
    print("USER CHANNEL - Real-time Order & Trade Updates")
    print("="*80 + "\n")
    
    def on_order(data):
        print(f"📋 Order Update: {data}")
    
    def on_trade(data):
        print(f"💰 Trade Update: {data}")
    
    ws = CLOBUserWebSocket(api_key, secret, passphrase)
    ws.subscribe(
        markets=["all"],  # Subscribe to all markets
        on_order=on_order,
        on_trade=on_trade,
    )
    
    print("Listening for user events... (Press Ctrl+C to stop)\n")
    
    try:
        ws.run(run_forever=True)
    except KeyboardInterrupt:
        print("\nStopping...")
        ws.close()


def market_channel_example():
    """Example: Subscribe to market channel for orderbook updates."""
    print("\n" + "="*80)
    print("MARKET CHANNEL - Real-time Orderbook Updates")
    print("="*80 + "\n")
    
    def on_book(data):
        buys = data.get("buys", [])[:3]
        sells = data.get("sells", [])[:3]
        print(f"\n📊 Orderbook Update:")
        print(f"   Top 3 Bids: {buys}")
        print(f"   Top 3 Asks: {sells}")
        print(f"   Spread: {data.get('bestAsk', 0) - data.get('bestBid', 0):.4f}")
    
    def on_price_change(data):
        print(f"💹 Price Change: {data.get('price')} ({data.get('side')}) - Size: {data.get('sizeChange')}")
    
    def on_last_trade(data):
        print(f"✅ Last Trade: {data.get('side').upper()} {data.get('size')} @ {data.get('price')}")
    
    # Example: Subscribe to specific asset IDs
    # You would get these from the Gamma API
    example_asset_ids = ["123456", "789012"]  # Replace with real asset IDs
    
    ws = CLOBMarketWebSocket()
    ws.subscribe_market(
        asset_ids=example_asset_ids,
        on_book=on_book,
        on_price_change=on_price_change,
        on_last_trade=on_last_trade,
    )
    
    print(f"Listening for market updates on assets: {example_asset_ids}")
    print("(Press Ctrl+C to stop)\n")
    
    try:
        ws.run(run_forever=True)
    except KeyboardInterrupt:
        print("\nStopping...")
        ws.close()


def crypto_prices_example():
    """Example: Subscribe to real-time crypto prices."""
    print("\n" + "="*80)
    print("CRYPTO PRICES - Real-time Price Feed")
    print("="*80 + "\n")
    
    def on_price_update(data):
        payload = data.get("payload", {})
        symbol = payload.get("symbol", "")
        value = payload.get("value", 0)
        timestamp = data.get("timestamp", 0)
        
        time_str = time.strftime("%H:%M:%S", time.localtime(timestamp / 1000))
        print(f"💵 {symbol.upper()}: ${value:,.2f} at {time_str}")
    
    ws = RTDSWebSocket()
    
    # Subscribe to Bitcoin and Ethereum prices from Binance
    ws.subscribe_crypto_prices(
        source="binance",
        pairs=["btc/usdt", "eth/usdt"],
        callback=on_price_update,
    )
    
    print("Listening for BTC and ETH prices... (Press Ctrl+C to stop)\n")
    
    try:
        ws.run(run_forever=True)
    except KeyboardInterrupt:
        print("\nStopping...")
        ws.close()


def comments_example():
    """Example: Subscribe to comment updates."""
    print("\n" + "="*80)
    print("COMMENTS - Real-time Comment Feed")
    print("="*80 + "\n")
    
    def on_comment(data):
        msg_type = data.get("type", "")
        payload = data.get("payload", {})
        
        if msg_type == "comment_created":
            body = payload.get("body", "")
            entity = payload.get("parentEntityType", "")
            print(f"💬 New comment on {entity}: {body[:100]}...")
        elif msg_type == "reaction_created":
            print(f"❤️  New reaction")
        elif msg_type == "comment_removed":
            print(f"🗑️  Comment removed")
    
    ws = RTDSWebSocket()
    ws.subscribe_comments(callback=on_comment)
    
    print("Listening for comments... (Press Ctrl+C to stop)\n")
    
    try:
        ws.run(run_forever=True)
    except KeyboardInterrupt:
        print("\nStopping...")
        ws.close()


def main():
    """Run WebSocket examples."""
    print("\n" + "="*80)
    print("POLYMARKET WEBSOCKET EXAMPLES")
    print("="*80)
    print("\nChoose an example:")
    print("1. User Channel (requires API credentials)")
    print("2. Market Channel")
    print("3. Crypto Prices")
    print("4. Comments")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        user_channel_example()
    elif choice == "2":
        market_channel_example()
    elif choice == "3":
        crypto_prices_example()
    elif choice == "4":
        comments_example()
    elif choice == "5":
        print("Goodbye!")
    else:
        print("Invalid choice. Please run again.")


if __name__ == "__main__":
    main()

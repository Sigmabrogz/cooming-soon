"""
Place Order Example
-------------------
Example of placing orders on Polymarket using the CLOB API.
Requires API credentials.
"""

import os
from dotenv import load_dotenv
from polymarket import PolymarketClient

load_dotenv()


def main():
    """Run place order example."""
    # Load credentials from environment
    private_key = os.getenv("PRIVATE_KEY")
    proxy_wallet = os.getenv("PROXY_WALLET_ADDRESS")
    api_key = os.getenv("POLY_API_KEY")
    secret = os.getenv("POLY_SECRET")
    passphrase = os.getenv("POLY_PASSPHRASE")
    
    if not all([private_key, proxy_wallet, api_key, secret, passphrase]):
        print("Error: Missing credentials in .env file")
        print("Required: PRIVATE_KEY, PROXY_WALLET_ADDRESS, POLY_API_KEY, POLY_SECRET, POLY_PASSPHRASE")
        return
    
    # Initialize client
    client = PolymarketClient(
        private_key=private_key,
        proxy_wallet_address=proxy_wallet,
        api_key=api_key,
        secret=secret,
        passphrase=passphrase,
    )
    
    print("\n" + "="*80)
    print("POLYMARKET ORDER PLACEMENT EXAMPLE")
    print("="*80 + "\n")
    
    # Example 1: Get active markets
    print("Fetching active markets...")
    markets = client.gamma.get_markets(closed=False, limit=5)
    
    if not markets:
        print("No active markets found.")
        return
    
    print("\nAvailable markets:")
    for i, market in enumerate(markets, 1):
        print(f"{i}. {market.get('title', 'Unknown')}")
        print(f"   Token ID: {market.get('token0Id', '')}")
        print(f"   Slug: {market.get('slug', '')}\n")
    
    # Example 2: Place a single order (DRY RUN - commented out for safety)
    print("\n" + "="*80)
    print("Example: Place Single Order")
    print("="*80)
    print("NOTE: This is a demonstration. Uncomment the code to place real orders.\n")
    
    example_token_id = markets[0].get("token0Id", "")
    
    print(f"""
    To place an order, you would call:
    
    order = client.clob.place_order(
        token_id="{example_token_id}",
        price=0.55,        # Price between 0 and 1
        size=10,           # Size in tokens
        side="BUY",        # "BUY" or "SELL"
        order_type="GTC",  # "GTC", "GTD", "FOK", or "FAK"
    )
    
    print(f"Order placed: {{order}}")
    """)
    
    # Uncomment to place a real order:
    # try:
    #     order = client.clob.place_order(
    #         token_id=example_token_id,
    #         price=0.55,
    #         size=10,
    #         side="BUY",
    #         order_type="GTC",
    #     )
    #     print(f"✅ Order placed successfully!")
    #     print(f"Order ID: {order.get('orderId')}")
    #     print(f"Order Hash: {order.get('orderHash')}")
    # except Exception as e:
    #     print(f"❌ Order failed: {e}")
    
    # Example 3: Get active orders
    print("\n" + "="*80)
    print("Fetching Active Orders")
    print("="*80 + "\n")
    
    try:
        active_orders = client.clob.get_active_orders(limit=10)
        
        if active_orders:
            print(f"Found {len(active_orders)} active orders:\n")
            for order in active_orders:
                print(f"Order ID: {order.get('orderId', 'N/A')}")
                print(f"Market: {order.get('market', 'N/A')}")
                print(f"Side: {order.get('side', 'N/A')}")
                print(f"Price: ${order.get('price', 0):.4f}")
                print(f"Size: {order.get('size', 0):.2f}")
                print(f"Status: {order.get('status', 'N/A')}")
                print("-" * 60)
        else:
            print("No active orders found.")
    except Exception as e:
        print(f"Error fetching orders: {e}")
    
    # Example 4: Cancel order (dry run)
    print("\n" + "="*80)
    print("Example: Cancel Order")
    print("="*80)
    print("""
    To cancel an order:
    
    result = client.clob.cancel_order(order_id="your_order_id")
    
    To cancel all orders:
    
    result = client.clob.cancel_all_orders()
    """)
    
    # Example 5: Batch orders
    print("\n" + "="*80)
    print("Example: Place Batch Orders")
    print("="*80)
    print("""
    To place multiple orders at once (up to 15):
    
    orders = [
        {
            "token_id": "123456",
            "price": 0.45,
            "size": 10,
            "side": "BUY",
            "order_type": "GTC"
        },
        {
            "token_id": "123456",
            "price": 0.65,
            "size": 15,
            "side": "SELL",
            "order_type": "GTC"
        },
    ]
    
    result = client.clob.place_batch_orders(orders)
    """)
    
    print("\n" + "="*80)
    print("Example complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

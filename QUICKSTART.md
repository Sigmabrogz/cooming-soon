# Quick Start Guide

Get started with the Polymarket SDK in minutes!

## Installation

1. **Clone/Download the repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
PRIVATE_KEY=your_wallet_private_key
PROXY_WALLET_ADDRESS=your_proxy_wallet_address
```

4. **Derive API credentials** (optional, for order placement)
```bash
python examples/derive_api_key.py
```

This will generate API credentials. Copy them to your `.env` file.

## Basic Usage Examples

### 1. Browse Markets

```python
from polymarket import PolymarketClient

client = PolymarketClient()

# Get top markets by volume
markets = client.gamma.get_markets(
    closed=False,
    limit=10,
    order="volume",
    ascending=False
)

for market in markets:
    print(f"{market['title']}")
    print(f"  Volume: ${market['volume']:,.2f}")
    print(f"  Liquidity: ${market['liquidity']:,.2f}\n")
```

### 2. Check Your Positions

```python
from polymarket import PolymarketClient

client = PolymarketClient()

positions = client.data.get_positions(
    user="your_proxy_wallet_address",
    closed=False
)

for pos in positions:
    print(f"{pos['market']['title']}")
    print(f"  Size: {pos['size']}")
    print(f"  P&L: ${pos['cashPnl']:.2f} ({pos['percentPnl']:.2f}%)\n")
```

### 3. View Trade History

```python
import time
from polymarket import PolymarketClient

client = PolymarketClient()

# Get trades from last 24 hours
yesterday = int(time.time()) - (24 * 60 * 60)

trades = client.data.get_trades(
    user="your_proxy_wallet_address",
    from_timestamp=yesterday,
    limit=50
)

for trade in trades:
    print(f"{trade['market']['title']}")
    print(f"  {trade['side']}: {trade['size']} @ ${trade['price']:.4f}\n")
```

### 4. Place an Order (requires API credentials)

```python
from polymarket import PolymarketClient

client = PolymarketClient(
    private_key="your_private_key",
    proxy_wallet_address="your_proxy_address",
    api_key="your_api_key",
    secret="your_secret",
    passphrase="your_passphrase"
)

# Place a buy order
order = client.clob.place_order(
    token_id="123456",  # Get from market data
    price=0.55,         # Price between 0 and 1
    size=10,            # Number of tokens
    side="BUY",         # BUY or SELL
    order_type="GTC"    # Good Till Cancelled
)

print(f"Order ID: {order['orderId']}")
```

### 5. Real-time Market Data

```python
from polymarket.websocket import CLOBMarketWebSocket

def on_price_update(data):
    print(f"New price: {data['price']}")

ws = CLOBMarketWebSocket()
ws.subscribe_market(
    asset_ids=["token_id"],
    on_price_change=on_price_update
)

ws.run()
```

## Run Example Scripts

The `examples/` directory contains complete, ready-to-run examples:

### Leaderboard
```bash
python examples/leaderboard.py
```
Shows top traders by volume and P&L over the last 24 hours.

### Wallet Tracker
```bash
python examples/wallet_tracker.py
```
Track a specific wallet's positions and activity with real-time updates.

### Market Dashboard
```bash
python examples/market_dashboard.py
```
Display market data, orderbook, and top holders with real-time updates.

### Place Orders
```bash
python examples/place_order_example.py
```
Interactive guide for placing orders (requires API credentials).

### WebSocket Streams
```bash
python examples/websocket_example.py
```
Interactive examples of all WebSocket streams.

## Common Tasks

### Get Market Information
```python
# Get market by slug
market = client.gamma.get_market_by_slug("trump-wins-2024")

# Get all markets for an event
markets = client.gamma.get_markets(event="event_id")
```

### Check Order Status
```python
# Get all active orders
orders = client.clob.get_active_orders()

# Get specific order
order = client.clob.get_order(order_hash="0x...")
```

### Cancel Orders
```python
# Cancel one order
client.clob.cancel_order(order_id="order_id")

# Cancel all orders
client.clob.cancel_all_orders()

# Cancel orders for specific market
client.clob.cancel_market_orders(market="market_slug")
```

### Get Portfolio Value
```python
portfolio = client.data.get_portfolio_value(
    user="your_wallet_address"
)
print(f"Total value: ${portfolio['value']:,.2f}")
```

## Need Help?

- Check the full documentation in `README.md`
- Review example scripts in `examples/`
- Read API documentation at https://docs.polymarket.com

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit `.env` file** - It contains your private keys
2. **Keep API credentials secure** - Don't share them
3. **Use environment variables** - Don't hardcode credentials
4. **Test with small amounts first** - Before placing large orders
5. **Monitor your positions** - Use the wallet tracker

## Next Steps

1. Run `python examples/market_dashboard.py` to explore markets
2. Set up API credentials to place orders
3. Build your own trading strategies using the SDK
4. Monitor positions with real-time WebSocket streams

Happy trading! 🚀

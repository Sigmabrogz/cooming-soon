# Project Structure

Complete overview of the Polymarket SDK codebase.

```
polybotw/
│
├── polymarket/                 # Core SDK package
│   ├── __init__.py            # Main client and package exports
│   ├── auth.py                # Authentication (L1/L2)
│   ├── clob.py                # CLOB API client (orders)
│   ├── data_api.py            # Data API client (positions, trades)
│   ├── gamma.py               # Gamma API client (markets, events)
│   ├── websocket.py           # WebSocket clients (real-time data)
│   ├── models.py              # Pydantic data models
│   └── exceptions.py          # Custom exceptions
│
├── examples/                   # Example scripts
│   ├── __init__.py
│   ├── leaderboard.py         # Top traders by P&L
│   ├── wallet_tracker.py      # Track wallet positions
│   ├── market_dashboard.py    # Market data dashboard
│   ├── place_order_example.py # Order placement guide
│   ├── websocket_example.py   # WebSocket streaming
│   └── derive_api_key.py      # Generate API credentials
│
├── requirements.txt           # Python dependencies
├── setup.py                   # Package installation script
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
│
├── README.md                  # Main documentation
├── QUICKSTART.md             # Quick start guide
├── API_REFERENCE.md          # Complete API reference
├── PROJECT_STRUCTURE.md      # This file
│
└── test_installation.py      # Installation verification
```

## Core Modules

### polymarket/__init__.py
Main entry point. Exports `PolymarketClient` class which provides unified access to all APIs.

**Key Classes:**
- `PolymarketClient`: Main client interface

### polymarket/auth.py
Authentication handler for both L1 (EIP-712) and L2 (API key) authentication.

**Key Classes:**
- `PolymarketAuth`: Handles signing and header generation

**Key Methods:**
- `sign_order()`: Sign orders with EIP-712
- `get_l2_headers()`: Generate authentication headers
- `derive_api_key()`: Get API credentials from wallet

### polymarket/clob.py
Central Limit Order Book API client for order management.

**Key Classes:**
- `CLOBClient`: Order placement and management

**Key Methods:**
- `place_order()`: Place single order
- `place_batch_orders()`: Place multiple orders
- `get_active_orders()`: List active orders
- `cancel_order()`: Cancel orders

### polymarket/data_api.py
Data API client for historical and current market data.

**Key Classes:**
- `DataAPIClient`: Access positions, trades, holders

**Key Methods:**
- `get_positions()`: Get user positions
- `get_trades()`: Get trade history
- `get_holders()`: Get token holders
- `get_portfolio_value()`: Get portfolio value

### polymarket/gamma.py
Gamma API client for market and event discovery.

**Key Classes:**
- `GammaAPIClient`: Access markets, events, tags

**Key Methods:**
- `get_markets()`: List markets
- `get_events()`: List events
- `get_market_by_slug()`: Get specific market
- `get_tags()`: Get market tags

### polymarket/websocket.py
WebSocket clients for real-time data streaming.

**Key Classes:**
- `CLOBUserWebSocket`: User order/trade updates
- `CLOBMarketWebSocket`: Market orderbook updates
- `RTDSWebSocket`: Crypto prices and comments

### polymarket/models.py
Pydantic models for type safety and validation.

**Key Models:**
- `Order`, `Position`, `Trade`
- `Market`, `Event`, `Holder`
- `OrderBook`, `PriceUpdate`, `CommentEvent`

**Key Enums:**
- `OrderSide`, `OrderType`, `OrderStatus`
- `ActivityType`

### polymarket/exceptions.py
Custom exception classes for error handling.

**Key Exceptions:**
- `PolymarketError`: Base exception
- `AuthenticationError`: Auth failures
- `OrderError`: Order failures
- `APIError`: API request failures
- `WebSocketError`: WebSocket failures

## Example Scripts

### examples/leaderboard.py
**Purpose:** Display top traders by volume and P&L

**Features:**
- Fetches trades from last 24 hours
- Calculates trader statistics
- Displays formatted leaderboard

**Usage:** `python examples/leaderboard.py`

### examples/wallet_tracker.py
**Purpose:** Track a specific wallet's activity

**Features:**
- Shows current positions with P&L
- Displays recent trades
- Real-time order/trade updates via WebSocket

**Usage:** `python examples/wallet_tracker.py`

**Requires:** `PROXY_WALLET_ADDRESS` in .env

### examples/market_dashboard.py
**Purpose:** Display market data and orderbook

**Features:**
- Lists top markets by volume
- Shows top holders
- Real-time orderbook updates via WebSocket

**Usage:** `python examples/market_dashboard.py`

### examples/place_order_example.py
**Purpose:** Demonstrate order placement

**Features:**
- Shows how to place orders
- Examples of batch orders
- Order cancellation examples

**Usage:** `python examples/place_order_example.py`

**Requires:** Full API credentials in .env

### examples/websocket_example.py
**Purpose:** Interactive WebSocket examples

**Features:**
- User channel (orders/trades)
- Market channel (orderbook)
- Crypto prices
- Comments feed

**Usage:** `python examples/websocket_example.py`

### examples/derive_api_key.py
**Purpose:** Generate API credentials

**Features:**
- Signs message with wallet
- Derives API key/secret/passphrase
- Displays credentials to add to .env

**Usage:** `python examples/derive_api_key.py`

**Requires:** `PRIVATE_KEY` in .env

## Documentation Files

### README.md
Main documentation with:
- Feature overview
- Installation instructions
- Quick start examples
- Project structure
- API reference links

### QUICKSTART.md
Quick start guide with:
- Step-by-step setup
- Basic usage examples
- Common tasks
- Example script descriptions
- Security best practices

### API_REFERENCE.md
Complete API reference with:
- Full method signatures
- Parameter descriptions
- Return types
- Code examples
- Error handling

### PROJECT_STRUCTURE.md
This file - complete project overview.

## Configuration Files

### requirements.txt
Python dependencies:
- `requests`: HTTP client
- `websocket-client`: WebSocket support
- `eth-account`: Ethereum signing
- `web3`: Web3 utilities
- `python-dotenv`: Environment variables
- `pydantic`: Data validation

### setup.py
Package installation configuration for pip.

### .gitignore
Git ignore patterns:
- Python cache files
- `.env` (secrets)
- IDE files
- OS files

### .env.example
Template for environment variables (not in repo, blocked by globalIgnore)

## Testing

### test_installation.py
Installation verification script that tests:
- Module imports
- Dependency installation
- Basic API connectivity

**Usage:** `python test_installation.py`

## Architecture

### Authentication Flow
```
Private Key → EIP-712 Signature → API Key/Secret/Passphrase
             ↓
         Sign Orders
             ↓
      L2 Headers (HMAC)
             ↓
         CLOB API
```

### Data Flow
```
PolymarketClient
    ├── CLOBClient → CLOB API (orders)
    ├── DataAPIClient → Data API (positions, trades)
    ├── GammaAPIClient → Gamma API (markets, events)
    └── WebSocket Clients → Real-time streams
```

### Error Handling
```
Try/Except
    ├── AuthenticationError → Credential issues
    ├── OrderError → Order placement issues
    ├── APIError → HTTP/API issues
    └── WebSocketError → Connection issues
```

## Best Practices

### Security
1. Never commit `.env` file
2. Use environment variables for secrets
3. Keep API credentials secure
4. Test with small amounts first

### Development
1. Use type hints
2. Handle exceptions properly
3. Close WebSocket connections
4. Implement retry logic for API calls

### Usage
1. Initialize client once
2. Reuse client instances
3. Monitor rate limits
4. Use WebSockets for real-time data

## Next Steps

1. **Install:** `pip install -r requirements.txt`
2. **Configure:** Copy `.env.example` to `.env`
3. **Test:** `python test_installation.py`
4. **Explore:** `python examples/market_dashboard.py`
5. **Build:** Create your own trading strategies!

## Support

- 📖 Documentation: See README.md and API_REFERENCE.md
- 💡 Examples: Check examples/ directory
- 🐛 Issues: Check error messages and exceptions
- 🔗 Official Docs: https://docs.polymarket.com

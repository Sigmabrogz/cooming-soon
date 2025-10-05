# Setup Instructions

Complete setup guide for the Polymarket SDK.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or with pip3:
```bash
pip3 install -r requirements.txt
```

### 2. Verify Installation

```bash
python test_installation.py
```

Expected output:
```
🎉 All tests passed! The SDK is ready to use.
```

### 3. Configure Environment Variables

Create a `.env` file (note: .env.example is blocked from creation in this workspace, so create it manually):

```bash
# Create .env file
touch .env
```

Add your credentials to `.env`:

```env
# Wallet Configuration
PRIVATE_KEY=your_wallet_private_key_here
PROXY_WALLET_ADDRESS=your_proxy_wallet_address_here

# API Credentials (optional, for order placement)
POLY_API_KEY=your_api_key_here
POLY_SECRET=your_secret_here
POLY_PASSPHRASE=your_passphrase_here
```

### 4. (Optional) Derive API Credentials

If you don't have API credentials yet:

```bash
python examples/derive_api_key.py
```

This will:
1. Sign a message with your private key
2. Generate API credentials
3. Display them for you to add to `.env`

## Quick Test

### Test 1: Fetch Markets (No Authentication Required)

```bash
python -c "
from polymarket import PolymarketClient
client = PolymarketClient()
markets = client.gamma.get_markets(limit=3)
for m in markets:
    print(f'{m[\"title\"]}: ${m.get(\"volume\", 0):,.0f}')
"
```

### Test 2: Run Example Dashboard

```bash
python examples/market_dashboard.py
```

### Test 3: Track a Wallet

```bash
# Add PROXY_WALLET_ADDRESS to .env first
python examples/wallet_tracker.py
```

## Troubleshooting

### Issue: "No module named 'requests'" (or similar)

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "command not found: python"

**Solution:** Use `python3` instead
```bash
python3 test_installation.py
python3 examples/market_dashboard.py
```

### Issue: "Failed to import PolymarketClient"

**Solution:** Make sure you're in the project directory
```bash
cd /path/to/polybotw
python test_installation.py
```

### Issue: "PRIVATE_KEY not set in .env file"

**Solution:** Create `.env` file with your credentials
```bash
# Create .env file
echo "PRIVATE_KEY=your_key_here" > .env
echo "PROXY_WALLET_ADDRESS=your_address_here" >> .env
```

### Issue: API connection errors

**Solution:** Check your internet connection and try again
- Polymarket APIs may be temporarily unavailable
- Check https://polymarket.com/ to verify service status

## Using a Virtual Environment (Recommended)

### Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Install in Virtual Environment

```bash
# After activating venv
pip install -r requirements.txt
```

### Deactivate Virtual Environment

```bash
deactivate
```

## Development Setup

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest (testing)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

### Run Tests

```bash
pytest
```

### Format Code

```bash
black polymarket/ examples/
```

### Check Types

```bash
mypy polymarket/
```

## Project Structure Overview

```
polybotw/
├── polymarket/          # Core SDK
├── examples/            # Example scripts
├── requirements.txt     # Dependencies
├── test_installation.py # Verify setup
└── [Documentation files]
```

## Next Steps

1. ✅ **Install dependencies** - `pip install -r requirements.txt`
2. ✅ **Test installation** - `python test_installation.py`
3. ✅ **Configure .env** - Add your credentials
4. 🚀 **Run examples** - Try `python examples/market_dashboard.py`
5. 📖 **Read docs** - Check QUICKSTART.md and API_REFERENCE.md
6. 🔨 **Build** - Create your own trading strategies!

## Getting Help

- **Quick Start**: See QUICKSTART.md
- **API Reference**: See API_REFERENCE.md
- **Examples**: Check examples/ directory
- **Official Docs**: https://docs.polymarket.com

## Security Reminders

⚠️ **IMPORTANT:**
- Never commit `.env` file (it's in .gitignore)
- Keep API credentials secure
- Don't share your private key
- Test with small amounts first
- Review all code before running with real funds

## Common Use Cases

### Read-Only Access (No Credentials Required)
- Browse markets
- View leaderboards
- Check market data
- View public positions

### With Proxy Wallet (PROXY_WALLET_ADDRESS)
- View your positions
- Track your trades
- Monitor portfolio value

### With API Credentials (Full Access)
- Place orders
- Cancel orders
- Real-time order updates
- Full trading functionality

## Support

If you encounter issues:
1. Check error messages carefully
2. Review this setup guide
3. Verify all dependencies are installed
4. Check that .env is configured correctly
5. Try running test_installation.py

Happy trading! 🎯

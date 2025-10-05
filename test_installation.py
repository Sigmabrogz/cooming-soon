"""
Installation Test Script
------------------------
Verify that the Polymarket SDK is installed correctly.
"""

import sys


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from polymarket import PolymarketClient
        print("✅ PolymarketClient imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PolymarketClient: {e}")
        return False
    
    try:
        from polymarket.auth import PolymarketAuth
        print("✅ PolymarketAuth imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PolymarketAuth: {e}")
        return False
    
    try:
        from polymarket.clob import CLOBClient
        print("✅ CLOBClient imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CLOBClient: {e}")
        return False
    
    try:
        from polymarket.data_api import DataAPIClient
        print("✅ DataAPIClient imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import DataAPIClient: {e}")
        return False
    
    try:
        from polymarket.gamma import GammaAPIClient
        print("✅ GammaAPIClient imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import GammaAPIClient: {e}")
        return False
    
    try:
        from polymarket.websocket import CLOBUserWebSocket, CLOBMarketWebSocket, RTDSWebSocket
        print("✅ WebSocket clients imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WebSocket clients: {e}")
        return False
    
    try:
        from polymarket.models import Order, Position, Trade, Market, Event
        print("✅ Models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Models: {e}")
        return False
    
    try:
        from polymarket.exceptions import PolymarketError, OrderError, APIError
        print("✅ Exceptions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Exceptions: {e}")
        return False
    
    return True


def test_dependencies():
    """Test that all required dependencies are installed."""
    print("\nTesting dependencies...")
    
    dependencies = [
        "requests",
        "websocket",
        "eth_account",
        "web3",
        "dotenv",
        "pydantic",
    ]
    
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} installed")
        except ImportError:
            print(f"❌ {dep} not installed")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def test_basic_functionality():
    """Test basic SDK functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from polymarket import PolymarketClient
        
        # Initialize client without credentials (read-only mode)
        client = PolymarketClient()
        print("✅ Client initialized successfully")
        
        # Test Gamma API (public endpoint)
        print("   Testing Gamma API...")
        markets = client.gamma.get_markets(limit=1)
        
        if markets and len(markets) > 0:
            print(f"✅ Fetched market data: {markets[0].get('title', 'Unknown')[:50]}...")
        else:
            print("⚠️  No market data returned (API may be temporarily unavailable)")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*80)
    print("POLYMARKET SDK INSTALLATION TEST")
    print("="*80 + "\n")
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test dependencies
    results.append(("Dependencies", test_dependencies()))
    
    # Test basic functionality
    results.append(("Basic Functionality", test_basic_functionality()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*80 + "\n")
    
    if all_passed:
        print("🎉 All tests passed! The SDK is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your credentials to .env")
        print("3. Run: python examples/market_dashboard.py")
        print("4. Check QUICKSTART.md for more examples")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure you've run: pip install -r requirements.txt")
        print("2. Check that you're using Python 3.8 or higher")
        print("3. Try creating a virtual environment")
        return 1


if __name__ == "__main__":
    sys.exit(main())

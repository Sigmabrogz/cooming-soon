"""
Simple Market Data Demo
-----------------------
Fetch and display Polymarket market data without any credentials.
No .env file or authentication needed!
"""

from polymarket import PolymarketClient


def main():
    """Fetch and display market data - no credentials required!"""
    
    print("\n" + "="*80)
    print("POLYMARKET MARKET DATA VIEWER")
    print("="*80)
    print("No credentials needed - fetching public data...\n")
    
    # Initialize client without any credentials (read-only mode)
    client = PolymarketClient()
    
    # 1. Get top markets by volume
    print("📊 Fetching top markets by volume...")
    try:
        markets = client.gamma.get_markets(
            closed=False,
            limit=10,
            order="volume",
            ascending=False
        )
        
        print(f"\n✅ Found {len(markets)} active markets\n")
        print("="*80)
        print("TOP 10 MARKETS BY VOLUME")
        print("="*80)
        print(f"{'#':<4}{'Market':<50}{'Volume':<15}{'Liquidity':<15}")
        print("-"*80)
        
        for i, market in enumerate(markets, 1):
            # Try different title fields
            title = (market.get('question') or 
                    market.get('title') or 
                    market.get('slug', 'Unknown').replace('-', ' ').title())[:48]
            volume = float(market.get('volume', 0) or 0)
            liquidity = float(market.get('liquidity', 0) or 0)
            
            print(f"{i:<4}{title:<50}${volume:>12,.0f}  ${liquidity:>12,.0f}")
        
        print("="*80 + "\n")
        
        # 2. Show details of the top market
        if markets:
            top_market = markets[0]
            featured_title = (top_market.get('question') or 
                            top_market.get('title') or 
                            top_market.get('slug', 'Unknown').replace('-', ' ').title())
            print("="*80)
            print(f"FEATURED MARKET: {featured_title}")
            print("="*80)
            print(f"Category: {top_market.get('category', 'N/A')}")
            print(f"Type: {top_market.get('type', 'N/A')}")
            print(f"Volume: ${float(top_market.get('volume', 0) or 0):,.2f}")
            print(f"Liquidity: ${float(top_market.get('liquidity', 0) or 0):,.2f}")
            print(f"End Date: {top_market.get('endDate', 'N/A')}")
            print(f"Slug: {top_market.get('slug', 'N/A')}")
            print(f"Condition ID: {top_market.get('conditionId', 'N/A')}")
            print("="*80 + "\n")
            
            # 3. Get holders for the top market
            print("👥 Fetching top holders...")
            try:
                condition_id = top_market.get('conditionId')
                holders_data = client.data.get_holders(market=condition_id, limit=10)
                # Handle both dict and list responses
                if isinstance(holders_data, dict):
                    holders = holders_data.get('holders', [])
                elif isinstance(holders_data, list):
                    holders = holders_data
                else:
                    holders = []
                
                if holders:
                    print(f"\n✅ Found {len(holders)} holders\n")
                    print("="*80)
                    print("TOP HOLDERS")
                    print("="*80)
                    print(f"{'Rank':<6}{'Wallet/Name':<50}{'Balance':<20}")
                    print("-"*80)
                    
                    for rank, holder in enumerate(holders, 1):
                        wallet = holder.get('proxyWallet', 'Unknown')
                        wallet_short = f"{wallet[:8]}...{wallet[-6:]}"
                        name = holder.get('name') or holder.get('pseudonym', 'Anonymous')
                        balance = holder.get('amount', 0)
                        
                        display = f"{wallet_short} ({name})" if name != "Anonymous" else wallet_short
                        display = display[:48]
                        
                        print(f"{rank:<6}{display:<50}{balance:>18,.2f}")
                    
                    print("="*80 + "\n")
                else:
                    print("No holder data available.\n")
                    
            except Exception as e:
                print(f"⚠️  Could not fetch holders: {e}\n")
        
        # 4. Get recent events
        print("📅 Fetching recent events...")
        try:
            events = client.gamma.get_events(
                closed=False,
                limit=5,
                order="volume",
                ascending=False
            )
            
            if events:
                print(f"\n✅ Found {len(events)} events\n")
                print("="*80)
                print("TOP EVENTS BY VOLUME")
                print("="*80)
                
                for i, event in enumerate(events, 1):
                    name = (event.get('title') or 
                           event.get('name') or 
                           event.get('slug', 'Unknown').replace('-', ' ').title())
                    volume = float(event.get('volume', 0) or 0)
                    liquidity = float(event.get('liquidity', 0) or 0)
                    slug = event.get('slug', 'N/A')
                    
                    print(f"\n{i}. {name}")
                    print(f"   Volume: ${volume:,.0f} | Liquidity: ${liquidity:,.0f}")
                    print(f"   Slug: {slug}")
                
                print("\n" + "="*80 + "\n")
                
        except Exception as e:
            print(f"⚠️  Could not fetch events: {e}\n")
        
        # 5. Summary
        total_volume = sum(float(m.get('volume', 0) or 0) for m in markets)
        total_liquidity = sum(float(m.get('liquidity', 0) or 0) for m in markets)
        
        print("="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Active Markets: {len(markets)}")
        print(f"Total Volume (Top 10): ${total_volume:,.2f}")
        print(f"Total Liquidity (Top 10): ${total_liquidity:,.2f}")
        print("="*80 + "\n")
        
        print("✨ Market data fetched successfully!")
        print("\n💡 Tips:")
        print("   - All data is public and requires no authentication")
        print("   - Run 'python examples/market_dashboard.py' for an interactive version")
        print("   - Check QUICKSTART.md for more examples\n")
        
    except Exception as e:
        print(f"❌ Error fetching market data: {e}")
        print("\nPossible reasons:")
        print("- No internet connection")
        print("- Polymarket API is temporarily unavailable")
        print("- Dependencies not installed (run: pip install -r requirements.txt)\n")


if __name__ == "__main__":
    main()

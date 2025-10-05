"""
Derive API Key Example
----------------------
Use your wallet private key to derive API credentials from Polymarket.
"""

import os
from dotenv import load_dotenv
from polymarket import PolymarketClient

load_dotenv()


def main():
    """Derive API key from private key."""
    private_key = os.getenv("PRIVATE_KEY")
    
    if not private_key:
        print("Error: PRIVATE_KEY not set in .env file")
        return
    
    print("\n" + "="*80)
    print("POLYMARKET API KEY DERIVATION")
    print("="*80 + "\n")
    
    print("Deriving API credentials from your wallet...")
    print("This will sign a message with your private key.\n")
    
    # Initialize client with just private key
    client = PolymarketClient(private_key=private_key)
    
    try:
        # Derive API key
        credentials = client.auth.derive_api_key(
            clob_url="https://clob.polymarket.com"
        )
        
        print("✅ API credentials derived successfully!\n")
        print("="*80)
        print("SAVE THESE CREDENTIALS TO YOUR .env FILE:")
        print("="*80)
        print(f"POLY_API_KEY={credentials['apiKey']}")
        print(f"POLY_SECRET={credentials['secret']}")
        print(f"POLY_PASSPHRASE={credentials['passphrase']}")
        print("="*80 + "\n")
        
        print("⚠️  IMPORTANT:")
        print("- Keep these credentials secure")
        print("- Do not share them with anyone")
        print("- Add them to your .env file (not .env.example)")
        print("- Make sure .env is in your .gitignore\n")
        
    except Exception as e:
        print(f"❌ Failed to derive API key: {e}")
        print("\nPossible reasons:")
        print("- Invalid private key")
        print("- Network connection issues")
        print("- Polymarket API unavailable\n")


if __name__ == "__main__":
    main()

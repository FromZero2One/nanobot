#!/usr/bin/env python3
"""Test script for market data tools."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_stock_price():
    """Test stock price tool."""
    from nanobot.agent.tools.market import StockPriceTool

    tool = StockPriceTool()

    print("=" * 60)
    print("Testing Stock Price Tool")
    print("=" * 60)

    # Test A-share
    print("\n1. Testing A-share (贵州茅台 600519)...")
    try:
        result = await tool.execute(symbol="600519", market="cn")
        print(result)
    except Exception as e:
        print(f"Error: {e}")

    # Test US stock
    print("\n2. Testing US stock (AAPL)...")
    try:
        result = await tool.execute(symbol="AAPL", market="us")
        print(result)
    except Exception as e:
        print(f"Error: {e}")

    # Test historical data
    print("\n3. Testing historical data (600519, 7 days)...")
    try:
        result = await tool.execute(
            symbol="600519", market="cn", period="daily", days=7
        )
        print(result)
    except Exception as e:
        print(f"Error: {e}")


async def test_crypto_price():
    """Test crypto price tool."""
    from nanobot.agent.tools.market import CryptoPriceTool

    tool = CryptoPriceTool()

    print("\n" + "=" * 60)
    print("Testing Crypto Price Tool")
    print("=" * 60)

    # Test BTC
    print("\n1. Testing Bitcoin (BTC)...")
    try:
        result = await tool.execute(symbol="BTC")
        print(result)
    except Exception as e:
        print(f"Error: {e}")

    # Test ETH
    print("\n2. Testing Ethereum (ETH)...")
    try:
        result = await tool.execute(symbol="ETH")
        print(result)
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all tests."""
    print("[TEST] Market Data Tools Test Suite")
    print("Using akshare for data retrieval\n")

    try:
        import akshare

        print(f"[OK] akshare version: {akshare.__version__}\n")
    except ImportError:
        print("[ERROR] akshare not installed. Run: pip install akshare\n")
        return

    await test_stock_price()
    await test_crypto_price()

    print("\n" + "=" * 60)
    print("[OK] All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

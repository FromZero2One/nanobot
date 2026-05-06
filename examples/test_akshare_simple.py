#!/usr/bin/env python3
"""Simple test for akshare market data (standalone, no nanobot dependencies)."""

import asyncio
from datetime import datetime


async def test_akshare_basic():
    """Test basic akshare functionality."""
    print("=" * 60)
    print("Testing akshare Market Data")
    print("=" * 60)

    try:
        import akshare as ak
        print(f"\n[OK] akshare version: {ak.__version__}\n")
    except ImportError as e:
        print(f"[ERROR] akshare not installed: {e}")
        return

    # Test 1: A-share real-time
    print("\n1. Testing A-share real-time data (贵州茅台 600519)...")
    try:
        df = ak.stock_zh_a_spot_em()
        stock_data = df[df['代码'] == '600519']

        if not stock_data.empty:
            row = stock_data.iloc[0]
            print(f"   Name: {row.get('名称', 'N/A')}")
            print(f"   Code: {row.get('代码', 'N/A')}")
            print(f"   Price: ¥{row.get('最新价', 0):.2f}")
            print(f"   Change: {row.get('涨跌幅', 0):.2f}%")
            print(f"   Volume: {row.get('成交量', 0):.0f}")
            print("[OK] A-share data retrieved successfully")
        else:
            print("[WARN] Stock not found (may be outside trading hours)")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Test 2: US stock
    print("\n2. Testing US stock (AAPL)...")
    try:
        df = ak.stock_us_spot_em()
        stock_data = df[df['代码'] == 'AAPL']

        if not stock_data.empty:
            row = stock_data.iloc[0]
            print(f"   Name: {row.get('名称', 'N/A')}")
            print(f"   Code: {row.get('代码', 'N/A')}")
            print(f"   Price: ${row.get('最新价', 0):.2f}")
            print(f"   Change: {row.get('涨跌幅', 0):.2f}%")
            print("[OK] US stock data retrieved successfully")
        else:
            print("[WARN] Stock not found")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Test 3: Crypto
    print("\n3. Testing cryptocurrency (BTC)...")
    try:
        df = ak.crypto_bitcoin_cmc()
        btc_data = df[df['symbol'] == 'bitcoin']

        if not btc_data.empty:
            row = btc_data.iloc[0]
            print(f"   Name: {row.get('name', 'Bitcoin')}")
            print(f"   Symbol: BTC")
            print(f"   Price: ${row.get('price', 0):,.2f}")
            print(f"   24h Change: {row.get('percent_change_24h', 0):.2f}%")
            print(f"   Market Cap: ${row.get('market_cap', 0):,.0f}")
            print("[OK] Crypto data retrieved successfully")
        else:
            print("[WARN] Crypto not found")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Test 4: Historical data
    print("\n4. Testing historical data (600519, last 7 days)...")
    try:
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")

        df = ak.stock_zh_a_hist(
            symbol="600519",
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )

        if not df.empty:
            print(f"   Records found: {len(df)}")
            print(f"   Date range: {df.iloc[0]['日期']} to {df.iloc[-1]['日期']}")
            print(f"   Latest close: ¥{df.iloc[-1]['收盘']:.2f}")
            print(f"   Highest: ¥{df['最高'].max():.2f}")
            print(f"   Lowest: ¥{df['最低'].min():.2f}")
            print("[OK] Historical data retrieved successfully")
        else:
            print("[WARN] No historical data found")
    except Exception as e:
        print(f"[ERROR] {e}")

    print("\n" + "=" * 60)
    print("[OK] All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_akshare_basic())

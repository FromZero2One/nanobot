"""Market data tools using akshare for stock/crypto analysis."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from loguru import logger

from nanobot.agent.tools.base import BaseTool


class StockPriceTool(BaseTool):
    """Get real-time and historical stock prices using akshare."""

    name = "stock_price"
    description = """获取股票实时价格和歷史数据。支持 A股、港股、美股。

Examples:
- stock_price(symbol="600519")  # 贵州茅台
- stock_price(symbol="AAPL", market="us")  # 苹果美股
- stock_price(symbol="00700", market="hk")  # 腾讯控股
- stock_price(symbol="600519", period="daily", days=30)  # 最近30天日线
"""

    def __init__(self):
        super().__init__()
        self._cache: dict[str, tuple[Any, float]] = {}
        self._cache_ttl = 60  # 60 seconds cache

    async def execute(
        self,
        symbol: str,
        market: str = "cn",
        period: str = "realtime",
        days: int = 30,
        **kwargs: Any,
    ) -> str:
        """
        Execute stock price query.

        Args:
            symbol: Stock code (e.g., "600519" for A-shares, "AAPL" for US stocks)
            market: Market type - "cn" (A股), "hk" (港股), "us" (美股)
            period: Data period - "realtime", "daily", "weekly", "monthly"
            days: Number of days for historical data (default: 30)

        Returns:
            Formatted stock price information
        """
        try:
            import akshare as ak
        except ImportError:
            return "Error: akshare not installed. Run: pip install akshare"

        cache_key = f"{symbol}_{market}_{period}_{days}"
        now = asyncio.get_event_loop().time()

        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if now - cached_time < self._cache_ttl:
                logger.debug("Using cached data for {}", symbol)
                return cached_data

        try:
            if period == "realtime":
                result = await self._get_realtime_price(ak, symbol, market)
            else:
                result = await self._get_historical_data(ak, symbol, market, period, days)

            # Cache the result
            self._cache[cache_key] = (result, now)
            return result

        except Exception as e:
            logger.error("Failed to get stock price for {}: {}", symbol, e)
            return f"Error fetching data for {symbol}: {str(e)}"

    async def _get_realtime_price(self, ak: Any, symbol: str, market: str) -> str:
        """Get real-time stock price."""
        try:
            if market == "cn":
                # A股实时行情
                df = ak.stock_zh_a_spot_em()
                stock_data = df[df['代码'] == symbol]

                if stock_data.empty:
                    return f"未找到股票代码: {symbol}"

                row = stock_data.iloc[0]
                return self._format_cn_stock(row)

            elif market == "hk":
                # 港股实时行情
                df = ak.stock_hk_spot_em()
                stock_data = df[df['代码'] == symbol]

                if stock_data.empty:
                    return f"未找到港股代码: {symbol}"

                row = stock_data.iloc[0]
                return self._format_hk_stock(row)

            elif market == "us":
                # 美股实时行情
                df = ak.stock_us_spot_em()
                stock_data = df[df['代码'] == symbol]

                if stock_data.empty:
                    return f"未找到美股代码: {symbol}"

                row = stock_data.iloc[0]
                return self._format_us_stock(row)

            else:
                return f"不支持的市场类型: {market} (支持: cn, hk, us)"

        except Exception as e:
            raise RuntimeError(f"Real-time price fetch failed: {e}")

    async def _get_historical_data(
        self, ak: Any, symbol: str, market: str, period: str, days: int
    ) -> str:
        """Get historical stock data."""
        try:
            if market == "cn":
                # A股历史数据
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"  # 前复权
                )

                if df.empty:
                    return f"未找到 {symbol} 的历史数据"

                return self._format_historical_cn(df, symbol, days)

            elif market == "us":
                # 美股历史数据
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

                df = ak.stock_us_hist(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )

                if df.empty:
                    return f"未找到 {symbol} 的历史数据"

                return self._format_historical_us(df, symbol, days)

            else:
                return f"暂不支持 {market} 市场的历史数据查询"

        except Exception as e:
            raise RuntimeError(f"Historical data fetch failed: {e}")

    def _format_cn_stock(self, row: pd.Series) -> str:
        """Format A-share stock data."""
        name = row.get('名称', 'N/A')
        code = row.get('代码', 'N/A')
        price = row.get('最新价', 0)
        change = row.get('涨跌幅', 0)
        change_amount = row.get('涨跌额', 0)
        volume = row.get('成交量', 0)
        amount = row.get('成交额', 0)
        high = row.get('最高', 0)
        low = row.get('最低', 0)
        open_price = row.get('今开', 0)
        prev_close = row.get('昨收', 0)

        # Format numbers
        volume_str = self._format_volume(volume)
        amount_str = self._format_amount(amount)

        # Determine trend emoji
        trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        change_sign = "+" if change > 0 else ""

        return f"""{trend} **{name} ({code})** - A股实时行情

💰 **当前价格**: ¥{price:.2f}
📊 **涨跌**: {change_sign}{change:.2f}% ({change_sign}{change_amount:.2f})

📈 **今日走势**:
• 开盘: ¥{open_price:.2f}
• 最高: ¥{high:.2f}
• 最低: ¥{low:.2f}
• 昨收: ¥{prev_close:.2f}

📦 **成交情况**:
• 成交量: {volume_str}
• 成交额: {amount_str}

⏰ **更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _format_hk_stock(self, row: pd.Series) -> str:
        """Format Hong Kong stock data."""
        name = row.get('名称', 'N/A')
        code = row.get('代码', 'N/A')
        price = row.get('最新价', 0)
        change = row.get('涨跌幅', 0)

        trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        change_sign = "+" if change > 0 else ""

        return f"""{trend} **{name} ({code})** - 港股实时行情

💰 **当前价格**: HK${price:.2f}
📊 **涨跌幅**: {change_sign}{change:.2f}%

⏰ **更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _format_us_stock(self, row: pd.Series) -> str:
        """Format US stock data."""
        name = row.get('名称', 'N/A')
        code = row.get('代码', 'N/A')
        price = row.get('最新价', 0)
        change = row.get('涨跌幅', 0)

        trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        change_sign = "+" if change > 0 else ""

        return f"""{trend} **{name} ({code})** - 美股实时行情

💰 **当前价格**: ${price:.2f}
📊 **涨跌幅**: {change_sign}{change:.2f}%

⏰ **更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _format_historical_cn(self, df: pd.DataFrame, symbol: str, days: int) -> str:
        """Format historical A-share data."""
        # Get basic info
        latest = df.iloc[-1]
        earliest = df.iloc[0]

        name = self._get_stock_name(symbol)
        current_price = latest['收盘']
        start_price = earliest['收盘']
        total_change = ((current_price - start_price) / start_price) * 100

        # Calculate statistics
        avg_price = df['收盘'].mean()
        max_price = df['最高'].max()
        min_price = df['最低'].min()
        avg_volume = df['成交量'].mean()

        trend = "📈" if total_change > 0 else "📉"
        change_sign = "+" if total_change > 0 else ""

        # Get recent 5 days
        recent = df.tail(5)
        recent_data = "\n".join([
            f"  • {row['日期']}: ¥{row['收盘']:.2f} ({'+' if row['涨跌幅'] > 0 else ''}{row['涨跌幅']:.2f}%)"
            for _, row in recent.iterrows()
        ])

        return f"""{trend} **{name} ({symbol})** - {days}日历史数据分析

📊 **价格概览**:
• 当前价格: ¥{current_price:.2f}
• {days}日前: ¥{start_price:.2f}
• 期间涨跌: {change_sign}{total_change:.2f}%

📈 **统计数据**:
• 平均价格: ¥{avg_price:.2f}
• 最高价: ¥{max_price:.2f}
• 最低价: ¥{min_price:.2f}
• 平均成交量: {self._format_volume(avg_volume)}

📅 **最近5个交易日**:
{recent_data}

⏰ **数据范围**: {earliest['日期']} 至 {latest['日期']}
"""

    def _format_historical_us(self, df: pd.DataFrame, symbol: str, days: int) -> str:
        """Format historical US stock data."""
        latest = df.iloc[-1]
        earliest = df.iloc[0]

        current_price = latest['收盘']
        start_price = earliest['收盘']
        total_change = ((current_price - start_price) / start_price) * 100

        trend = "📈" if total_change > 0 else "📉"
        change_sign = "+" if total_change > 0 else ""

        recent = df.tail(5)
        recent_data = "\n".join([
            f"  • {row['日期']}: ${row['收盘']:.2f} ({'+' if row['涨跌幅'] > 0 else ''}{row['涨跌幅']:.2f}%)"
            for _, row in recent.iterrows()
        ])

        return f"""{trend} **{symbol}** - {days}日历史数据分析

📊 **价格概览**:
• 当前价格: ${current_price:.2f}
• {days}日前: ${start_price:.2f}
• 期间涨跌: {change_sign}{total_change:.2f}%

📅 **最近5个交易日**:
{recent_data}

⏰ **数据范围**: {earliest['日期']} 至 {latest['日期']}
"""

    def _get_stock_name(self, symbol: str) -> str:
        """Get stock name by symbol (simplified)."""
        # This could be enhanced with a proper stock info lookup
        stock_names = {
            "600519": "贵州茅台",
            "000858": "五粮液",
            "600036": "招商银行",
            "000333": "美的集团",
            "601318": "中国平安",
        }
        return stock_names.get(symbol, f"股票{symbol}")

    @staticmethod
    def _format_volume(volume: float) -> str:
        """Format volume number."""
        if volume >= 1_0000_0000:
            return f"{volume / 1_0000_0000:.2f}亿手"
        elif volume >= 1_0000:
            return f"{volume / 1_0000:.2f}万手"
        else:
            return f"{volume:.0f}手"

    @staticmethod
    def _format_amount(amount: float) -> str:
        """Format amount number."""
        if amount >= 1_0000_0000:
            return f"¥{amount / 1_0000_0000:.2f}亿"
        elif amount >= 1_0000:
            return f"¥{amount / 1_0000:.2f}万"
        else:
            return f"¥{amount:.2f}"


class CryptoPriceTool(BaseTool):
    """Get cryptocurrency prices using akshare."""

    name = "crypto_price"
    description = """获取加密货币实时价格。支持 BTC, ETH, SOL 等主流币种。

Examples:
- crypto_price(symbol="BTC")  # 比特币
- crypto_price(symbol="ETH")  # 以太坊
- crypto_price(symbol="SOL")  # Solana
"""

    async def execute(self, symbol: str, **kwargs: Any) -> str:
        """Get crypto price."""
        try:
            import akshare as ak
        except ImportError:
            return "Error: akshare not installed. Run: pip install akshare"

        try:
            # Use Binance spot prices
            df = ak.crypto_bitcoin_cmc()

            # Normalize symbol
            symbol_upper = symbol.upper()
            symbol_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "BNB": "binancecoin",
                "XRP": "ripple",
                "ADA": "cardano",
                "DOGE": "dogecoin",
            }

            normalized = symbol_map.get(symbol_upper, symbol_lower())

            # Find the crypto
            crypto_data = df[df['symbol'] == normalized]

            if crypto_data.empty:
                return f"未找到加密货币: {symbol}\n支持的币种: {', '.join(symbol_map.keys())}"

            row = crypto_data.iloc[0]
            return self._format_crypto(row, symbol_upper)

        except Exception as e:
            logger.error("Failed to get crypto price for {}: {}", symbol, e)
            return f"Error fetching crypto data for {symbol}: {str(e)}"

    def _format_crypto(self, row: pd.Series, symbol: str) -> str:
        """Format cryptocurrency data."""
        name = row.get('name', symbol)
        price = row.get('price', 0)
        change_24h = row.get('percent_change_24h', 0)
        market_cap = row.get('market_cap', 0)
        volume_24h = row.get('volume_24h', 0)

        trend = "📈" if change_24h > 0 else "📉" if change_24h < 0 else "➡️"
        change_sign = "+" if change_24h > 0 else ""

        return f"""{trend} **{name} ({symbol})** - 加密货币实时价格

💰 **当前价格**: ${price:,.2f}
📊 **24h涨跌**: {change_sign}{change_24h:.2f}%

📈 **市场数据**:
• 市值: ${market_cap:,.0f}
• 24h成交量: ${volume_24h:,.0f}

⏰ **更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

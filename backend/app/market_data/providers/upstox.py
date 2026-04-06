"""
app/market_data/providers/upstox.py

Upstox API v2 provider — Indian market (NSE/BSE) quotes,
OHLCV data, and market depth (order book).
Uses KeyRotatorRegistry for automatic key rotation.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

from app.market_data.key_rotator import KeyRotatorRegistry
from app.schemas.market import MarketDepth, OHLCVPoint, StockQuote, Market

logger = logging.getLogger(__name__)

BASE_URL = "https://api.upstox.com/v2"
TIMEOUT = 12.0


def _build_instrument_key(symbol: str, exchange: str = "NSE_EQ") -> str:
    """
    Convert plain symbol → Upstox instrument key.
    e.g. "HINDCOPPER" → "NSE_EQ|HINDCOPPER"
    Override exchange for BSE: "BSE_EQ|SYMBOL"
    """
    return f"{exchange}|{symbol.upper()}"


def _auth_headers(key: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {key}", "Accept": "application/json"}


class UpstoxProvider:
    """
    Stateless Upstox provider.
    Key management → KeyRotatorRegistry.upstox
    """

    # ------------------------------------------------------------------
    # Real-time Quote
    # ------------------------------------------------------------------

    @staticmethod
    async def get_quote(symbol: str, exchange: str = "NSE_EQ") -> Optional[StockQuote]:
        """Fetch real-time LTP + OHLC quote for an Indian stock."""
        if not KeyRotatorRegistry.upstox:
            logger.error("[Upstox] KeyRotatorRegistry not initialized. Call init_market_services() at startup.")
            return None
        
        key = KeyRotatorRegistry.upstox.get_key()
        if not key:
            logger.error("[Upstox] No available API key.")
            return None

        instrument_key = _build_instrument_key(symbol, exchange)

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                resp = await client.get(
                    f"{BASE_URL}/market-quote/quotes",
                    headers=_auth_headers(key),
                    params={"instrument_key": instrument_key},
                )

                if resp.status_code == 429:
                    logger.warning("[Upstox] 429 — rotating key.")
                    KeyRotatorRegistry.upstox.mark_exhausted(key)
                    return await UpstoxProvider.get_quote(symbol, exchange)

                if resp.status_code == 401:
                    logger.error(f"[Upstox] 401 Unauthorised — key …{key[-6:]} may be expired.")
                    KeyRotatorRegistry.upstox.mark_exhausted(key)
                    return None

                resp.raise_for_status()
                body = resp.json()

                if body.get("status") != "success":
                    logger.warning(f"[Upstox] Non-success status: {body}")
                    return None

                q = body["data"].get(instrument_key, {})
                ltp = float(q.get("last_price", 0))
                prev_close = float(q.get("prev_close_price") or q.get("ohlc", {}).get("close", ltp))
                change = ltp - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0.0

                ohlc = q.get("ohlc", {})

                return StockQuote(
                    symbol=symbol.upper(),
                    price=ltp,
                    change=round(change, 2),
                    change_percent=round(change_pct, 2),
                    volume=int(q.get("volume", 0)),
                    high=float(ohlc.get("high", 0)),
                    low=float(ohlc.get("low", 0)),
                    open=float(ohlc.get("open", 0)),
                    prev_close=prev_close,
                    timestamp=q.get("last_trade_time", ""),
                    market=Market.INDIA,
                )

            except httpx.TimeoutException:
                logger.error(f"[Upstox] Timeout for {symbol}")
                return None
            except Exception as exc:
                logger.exception(f"[Upstox] Quote error for {symbol}: {exc}")
                return None

    # ------------------------------------------------------------------
    # Market Depth (Order Book)
    # ------------------------------------------------------------------

    @staticmethod
    async def get_market_depth(symbol: str, exchange: str = "NSE_EQ") -> Optional[MarketDepth]:
        """
        Fetch top-5 bid/ask order book.
        Returns MarketDepth with buy_orders, sell_orders, buy_pct, sell_pct.
        """
        if not KeyRotatorRegistry.upstox:
            logger.error("[Upstox] KeyRotatorRegistry not initialized. Call init_market_services() at startup.")
            return None
        
        key = KeyRotatorRegistry.upstox.get_key()
        if not key:
            return None

        instrument_key = _build_instrument_key(symbol, exchange)

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                resp = await client.get(
                    f"{BASE_URL}/market-quote/quotes",
                    headers=_auth_headers(key),
                    params={"instrument_key": instrument_key},
                )

                if resp.status_code == 429:
                    KeyRotatorRegistry.upstox.mark_exhausted(key)
                    return await UpstoxProvider.get_market_depth(symbol, exchange)

                resp.raise_for_status()
                body = resp.json()

                if body.get("status") != "success":
                    return None

                q = body["data"].get(instrument_key, {})
                depth = q.get("depth", {})

                buy_orders: List[Dict] = depth.get("buy", [])[:5]
                sell_orders: List[Dict] = depth.get("sell", [])[:5]

                total_buy_qty = sum(o.get("quantity", 0) for o in buy_orders)
                total_sell_qty = sum(o.get("quantity", 0) for o in sell_orders)
                total_qty = total_buy_qty + total_sell_qty

                return MarketDepth(
                    symbol=symbol.upper(),
                    buy_orders=buy_orders,
                    sell_orders=sell_orders,
                    buy_percentage=round((total_buy_qty / total_qty * 100) if total_qty else 0, 2),
                    sell_percentage=round((total_sell_qty / total_qty * 100) if total_qty else 0, 2),
                )

            except Exception as exc:
                logger.exception(f"[Upstox] MarketDepth error for {symbol}: {exc}")
                return None

    # ------------------------------------------------------------------
    # Historical OHLCV
    # ------------------------------------------------------------------

    @staticmethod
    async def get_historical(
        symbol: str,
        interval: str = "1minute",
        exchange: str = "NSE_EQ",
        from_date: str = "",
        to_date: str = "",
    ) -> List[OHLCVPoint]:
        """
        Fetch historical candles from Upstox.
        interval: 1minute, 30minute, 1day, 1week, 1month
        """
        from datetime import date, timedelta

        if not KeyRotatorRegistry.upstox:
            logger.error("[Upstox] KeyRotatorRegistry not initialized. Call init_market_services() at startup.")
            return []
        
        key = KeyRotatorRegistry.upstox.get_key()
        if not key:
            return []

        if not to_date:
            to_date = date.today().isoformat()
        if not from_date:
            from_date = (date.today() - timedelta(days=7)).isoformat()

        instrument_key = _build_instrument_key(symbol, exchange)
        url = (
            f"{BASE_URL}/historical-candle/"
            f"{instrument_key}/{interval}/{to_date}/{from_date}"
        )

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(url, headers=_auth_headers(key))

                if resp.status_code == 429:
                    KeyRotatorRegistry.upstox.mark_exhausted(key)
                    return await UpstoxProvider.get_historical(
                        symbol, interval, exchange, from_date, to_date
                    )

                resp.raise_for_status()
                body = resp.json()

                candles: List[Any] = body.get("data", {}).get("candles", [])

                return [
                    OHLCVPoint(
                        timestamp=c[0],
                        open=float(c[1]),
                        high=float(c[2]),
                        low=float(c[3]),
                        close=float(c[4]),
                        volume=int(c[5]),
                    )
                    for c in candles
                ]

            except Exception as exc:
                logger.exception(f"[Upstox] Historical error for {symbol}: {exc}")
                return []

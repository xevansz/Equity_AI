import asyncio
import logging
import time

from fastapi import APIRouter, HTTPException, Request

from app.market_data.key_rotator import KeyRotatorRegistry
from app.schemas.market import Market
from app.schemas.search import BatchSearchRequest, SearchQuery, UnifiedSearchResponse
from app.utils.market_resolver import resolve_market_from_symbol
from app.utils.market_utils import get_market_status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["unified_search"])


@router.post("/stock", response_model=UnifiedSearchResponse)
async def search_stock(query: SearchQuery, request: Request):

    dispatcher = request.app.state.market_dispatcher
    start = time.perf_counter()

    symbol_input = query.query.strip().upper()

    # AUTO MARKET DETECTION
    market, exchange, symbol = resolve_market_from_symbol(symbol_input)

    logger.info(f"Resolved {symbol} → {market} / {exchange}")

    tasks = {}

    # QUOTE (REQUIRED)
    tasks["quote"] = dispatcher.get_quote(symbol, market, exchange.value)

    # OPTIONAL DATA
    if query.include_chart:
        tasks["chart"] = dispatcher.get_chart(symbol, query.interval.value, query.chart_size, market, exchange.value)

    if query.include_fundamentals:
        tasks["fundamentals"] = dispatcher.get_fundamentals(symbol, market)

    if query.include_depth and market == Market.INDIA:
        tasks["depth"] = dispatcher.get_market_depth(symbol, exchange.value)

    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    data = dict(zip(tasks.keys(), results, strict=False))

    # REMOVE MOCK — THROW ERROR IF NO REAL DATA
    quote = data.get("quote")

    if isinstance(quote, Exception) or not quote:
        logger.error(f"Real quote failed: {quote}")
        raise HTTPException(503, f"Real market data unavailable for {symbol}. Check API keys or provider.")

    elapsed = (time.perf_counter() - start) * 1000

    return UnifiedSearchResponse(
        symbol=symbol,
        market=market,
        exchange=exchange,
        market_status=get_market_status(market),
        quote=quote.__dict__ if hasattr(quote, "__dict__") else quote,
        chart=[c.__dict__ for c in data.get("chart", [])]
        if data.get("chart") and not isinstance(data.get("chart"), Exception)
        else None,
        fundamentals=data.get("fundamentals") if not isinstance(data.get("fundamentals"), Exception) else None,
        depth=data.get("depth").__dict__
        if data.get("depth") and not isinstance(data.get("depth"), Exception)
        else None,
        processing_time_ms=round(elapsed, 2),
    )


@router.post("/batch")
async def search_batch(batch_request: BatchSearchRequest, request: Request):
    """Batch search for multiple stock symbols.

    Args:
        batch_request: Batch search request with list of queries
        request: FastAPI request object

    Returns:
        Dictionary with results and total count
    """
    queries = batch_request.queries

    tasks = [search_stock(SearchQuery(query=q), request) for q in queries]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful_results = []
    failed_results = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed_results.append({"query": queries[i], "error": str(result)})
        else:
            successful_results.append(result)

    return {
        "results": successful_results,
        "failed": failed_results,
        "total": len(queries),
        "successful": len(successful_results),
        "failed_count": len(failed_results),
    }


@router.get("/stats")
async def get_stats():

    return {
        "twelve_data": KeyRotatorRegistry.twelve_data.get_stats() if KeyRotatorRegistry.twelve_data else {},
        "upstox": KeyRotatorRegistry.upstox.get_stats() if KeyRotatorRegistry.upstox else {},
    }

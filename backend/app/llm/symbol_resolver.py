import re

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.llm.gemini import gemini
from app.logging_config import get_logger
from app.services.symbol_cache_service import SymbolCacheService
from app.utils.normalization import looks_like_ticker

logger = get_logger(__name__)

SYMBOL_RESOLUTION_PROMPT = """
You are a financial entity resolver.

Extract the company name and stock ticker symbol from the query.

Return format: COMPANY_NAME|SYMBOL

Rules:
- Return ONLY in format: CompanyName|TICKER
- No explanation, punctuation, extra words.
- Uppercase letters only.
- If multiple companies are mentioned, return the main company.
- If no public company is found, return: UNKNOWN

Examples:

Query: "Should I invest in Apple?"
Answer: Apple|AAPL

Query: "Tesla earnings report"
Answer: Tesla|TSLA

Query: "Microsoft vs Google stock"
Answer: Microsoft|MSFT

Query: "Tell me about gold prices"
Answer: UNKNOWN

Now resolve this:

Question: "{query}"
Answer:
"""


def normalize_symbol(raw: str) -> str:
    raw = raw.strip().upper()
    match = re.search(r"\b[A-Z]{1,6}\b", raw)
    if match:
        return match.group(0)
    return "UNKNOWN"


async def symbol_resolver(query: str, db: AsyncIOMotorDatabase) -> tuple[str, str]:
    """Resolve symbol with caching. Returns (symbol, company_name) tuple."""

    cache_service = SymbolCacheService(db)

    # If the user directly provided a ticker, return it immediately
    if looks_like_ticker(query):
        ticker = query.strip().upper()
        logger.info("Query looks like ticker, skipping resolver: %s", ticker)
        # Check if we have company name in cache for this ticker
        cached_symbol, cached_company = await cache_service.get_symbol(query)
        if cached_symbol:
            return cached_symbol, cached_company
        # No cache hit, return ticker for both (will be used for stock, news will be less specific)
        return ticker, ticker

    # Search in cache first for company name queries
    cached_symbol, cached_company = await cache_service.get_symbol(query)
    if cached_symbol and cached_company:
        logger.info("Symbol found in cache: %s -> %s", cached_symbol, cached_company)
        return cached_symbol, cached_company

    # Fallback to LLM if not found in cache
    try:
        prompt = SYMBOL_RESOLUTION_PROMPT.format(query=query)
        response = await gemini.generate(prompt)

        parts = response.strip().split("|")
        if len(parts) == 2:
            company_name, symbol = parts
            symbol = normalize_symbol(symbol)

            if symbol != "UNKNOWN":
                await cache_service.cache_alias(company_name.strip(), symbol)
                logger.debug("Symbol cached successfully: %s -> %s", symbol, company_name.strip())
            return symbol, company_name.strip()

        else:
            logger.info("Symbol not found")
            return "UNKNOWN", "UNKNOWN"

    except Exception as e:
        logger.exception("Symbol resolution failed: %s", str(e))
        return "UNKNOWN", "UNKNOWN"

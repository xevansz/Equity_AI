from app.llm.gemini import gemini
import re
from app.services.symbol_cache_service import SymbolCacheService

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


async def symbol_resolver(query: str, db):
  """resolve symbol with caching"""
  cache_service = SymbolCacheService(db)

  # search in cache first
  cached_symbol = await cache_service.get_symbol(query)
  if cached_symbol:
    print(f"symbol found in cache: {cached_symbol}")
    return cached_symbol

  # fallback to LLM if not found in cache
  try:
    prompt = SYMBOL_RESOLUTION_PROMPT.format(query=query)
    response = await gemini.generate(prompt)

    parts = response.strip().split("|")
    if len(parts) == 2:
      company_name, symbol = parts
      symbol = normalize_symbol(symbol)

      if symbol != "UNKNOWN":
        await cache_service.cache_symbol(company_name.strip(), symbol)
        print("cached succesfully")
      return symbol

    else:
      print("symbol not found")
      return "UNKNOWN"

  except Exception as e:
    print(f"Symbol resolution failed: {e}")
    return "UNKNOWN"

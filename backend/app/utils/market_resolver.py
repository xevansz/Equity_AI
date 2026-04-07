import re

from app.schemas.market import Exchange, Market


def resolve_market_from_symbol(symbol: str) -> tuple[Market, Exchange, str]:
    """
    Resolve market and exchange from a symbol string.
    
    Handles formats like:
    - AAPL → US/NASDAQ
    - RELIANCE.NS → INDIA/NSE
    - HINDCOPPER → INDIA/NSE (if no suffix, assume NSE for Indian-looking symbols)
    - TSLA → US/NASDAQ
    
    Returns:
        tuple: (market, exchange, clean_symbol)
    """
    symbol = symbol.strip().upper()
    
    # Check for explicit exchange suffixes
    if symbol.endswith('.NS') or symbol.endswith('.NSE'):
        clean_symbol = re.sub(r'\.(NS|NSE)$', '', symbol)
        return Market.INDIA, Exchange.NSE_EQ, clean_symbol
    
    if symbol.endswith('.BO') or symbol.endswith('.BSE'):
        clean_symbol = re.sub(r'\.(BO|BSE)$', '', symbol)
        return Market.INDIA, Exchange.BSE_EQ, clean_symbol
    
    # Indian stock symbols are typically longer and may contain specific patterns
    # For now, default to US market for symbols without explicit suffix
    # You can enhance this logic based on your needs
    
    return Market.US, Exchange.NASDAQ, symbol

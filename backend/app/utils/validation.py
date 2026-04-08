"""Shared validation utilities"""

import re


def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol format.
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        True if symbol is valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Allow alphanumeric characters, dots, hyphens, and colons
    # Common formats: AAPL, BRK.B, NSE:RELIANCE, etc.
    return bool(re.match(r"^[A-Z0-9.\-:]+$", symbol.strip().upper()))


def normalize_symbol(symbol: str) -> str:
    """Normalize symbol to uppercase and strip whitespace.
    
    Args:
        symbol: Stock symbol to normalize
        
    Returns:
        Normalized symbol
    """
    return symbol.strip().upper()

from datetime import datetime, time

from app.schemas.market import Market


def get_market_status(market: Market) -> dict:
    """
    Get current market status (open/closed) based on market and current time.
    
    Returns:
        dict: {"status": "open"|"closed", "market": str, "next_open": str|None}
    """
    now = datetime.utcnow()
    current_time = now.time()
    
    if market == Market.US:
        # US market hours: 9:30 AM - 4:00 PM EST (14:30 - 21:00 UTC)
        market_open = time(14, 30)
        market_close = time(21, 0)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return {
                "status": "closed",
                "market": "US",
                "reason": "weekend",
                "next_open": "Monday 9:30 AM EST"
            }
        
        if market_open <= current_time <= market_close:
            return {"status": "open", "market": "US"}
        else:
            return {
                "status": "closed",
                "market": "US",
                "reason": "after_hours",
                "next_open": "9:30 AM EST"
            }
    
    elif market == Market.INDIA:
        # Indian market hours: 9:15 AM - 3:30 PM IST (3:45 - 10:00 UTC)
        market_open = time(3, 45)
        market_close = time(10, 0)
        
        # Check if it's a weekday
        if now.weekday() >= 5:
            return {
                "status": "closed",
                "market": "INDIA",
                "reason": "weekend",
                "next_open": "Monday 9:15 AM IST"
            }
        
        if market_open <= current_time <= market_close:
            return {"status": "open", "market": "INDIA"}
        else:
            return {
                "status": "closed",
                "market": "INDIA",
                "reason": "after_hours",
                "next_open": "9:15 AM IST"
            }
    
    return {"status": "unknown", "market": str(market)}

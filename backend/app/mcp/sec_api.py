"""SEC Filings API"""

from app.mcp.base import BaseMCP


class SECAPI(BaseMCP):
    def __init__(self):
        super().__init__("https://www.sec.gov/cgi-bin/browse-edgar")

    async def get_filings(self, ticker: str):
        # Simplified SEC API call
        return {"ticker": ticker, "filings": []}


sec_api = SECAPI()

"""Research Service"""

from ingestion.financial_loader import financial_loader
from research_engine.financial_analysis import financial_analyzer
from research_engine.report_generator import report_generator
from schemas.research import ResearchResponse


class ResearchService:
    def __init__(self, db):
        self.db = db

    async def generate_report(self, symbol: str):
        # Load financial data
        financials = await financial_loader.load_financials(symbol)

        # Analyze
        analysis = financial_analyzer.analyze_liquidity(
            financials.get("balance_sheet", {})
        )

        # Generate report
        report = await report_generator.generate_report(symbol, {"financial": analysis})

        return ResearchResponse(symbol=symbol, report=report, analysis=analysis)

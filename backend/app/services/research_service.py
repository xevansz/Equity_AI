"""Research Service"""

from app.ingestion.financial_loader import FinancialLoader
from app.llm import report_generator
from app.research_engine.financial_analysis import financial_analyzer
from app.schemas.research import ResearchResponse


class ResearchService:
    def __init__(self, db, financial_loader: FinancialLoader):
        self.db = db
        self._financial_loader = financial_loader

    async def generate_report(self, symbol: str):
        # Load financial data
        financials = await self._financial_loader.load_financials(symbol)

        # Analyze
        analysis = financial_analyzer.analyze_liquidity(financials.get("balance_sheet", {}))

        # Generate report
        report = await report_generator.generate_report(symbol, {"financial": analysis})

        return ResearchResponse(symbol=symbol, report=report, analysis=analysis)

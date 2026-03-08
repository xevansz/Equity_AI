from app.llm.gemini import gemini
from app.research_engine.financial_analysis import analyze_financials
from app.research_engine.growth_analysis import analyze_growth
from app.research_engine.risk_analysis import analyze_risks
from app.research_engine.valuation_engine import analyze_valuation


def generate_equity_report(symbol: str):
    data_cot = analyze_financials(symbol)
    thesis_cot = analyze_growth(symbol)
    valuation = analyze_valuation(symbol)
    risk_cot = analyze_risks(symbol)

    return {
        "symbol": symbol,
        "Data_CoT": data_cot,
        "Thesis_CoT": thesis_cot,
        "Valuation": valuation,
        "Risk_CoT": risk_cot,
    }


class ReportGenerator:
    async def generate_report(self, symbol: str, analysis_data: dict):
        prompt = f"""
        Generate a comprehensive equity research report for {symbol}:
        
        Financial Analysis: {analysis_data.get("financial")}
        Growth Analysis: {analysis_data.get("growth")}
        Risk Assessment: {analysis_data.get("risk")}
        Valuation: {analysis_data.get("valuation")}
        
        Provide executive summary, detailed analysis, and recommendation.
        """

        report = await gemini.generate(prompt)
        return report


report_generator = ReportGenerator()

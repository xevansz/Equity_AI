def clean_rate_limit(data: dict):
    """Remove Alpha Vantage rate-limit responses"""
    if isinstance(data, dict) and "Information" in data:
        return {}
    return data


def calculate_top_metrics(financials: dict):
    """
    Calculate top 10 equity metrics safely
    """

    income = financials.get("income_statement") or {}
    balance = financials.get("balance_sheet") or {}
    cashflow = financials.get("cash_flow") or {}

    def safe_div(a, b):
        try:
            return round(a / b, 4) if a is not None and b not in (0, None) else None
        except Exception as e:
            print(f"Error: {e}")
            return None

    revenue = income.get("totalRevenue")
    net_income = income.get("netIncome")
    operating_income = income.get("operatingIncome")
    total_assets = balance.get("totalAssets")
    total_equity = balance.get("totalShareholderEquity")
    total_liabilities = balance.get("totalLiabilities")
    current_assets = balance.get("totalCurrentAssets")
    current_liabilities = balance.get("totalCurrentLiabilities")
    free_cash_flow = cashflow.get("freeCashFlow")
    shares_outstanding = income.get("weightedAverageShsOut")

    metrics = {
        "Revenue": revenue,
        "Net_Income": net_income,
        "EPS": safe_div(net_income, shares_outstanding),
        "ROE": safe_div(net_income, total_equity),
        "ROA": safe_div(net_income, total_assets),
        "Operating_Margin": safe_div(operating_income, revenue),
        "Debt_to_Equity": safe_div(total_liabilities, total_equity),
        "Current_Ratio": safe_div(current_assets, current_liabilities),
        "Free_Cash_Flow": free_cash_flow,
        "PE_Ratio": None,  # needs market price (optional)
    }

    return metrics

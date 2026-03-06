"""Financial Prompt Templates"""

FINANCIAL_ANALYSIS_PROMPT = """
Analyze the following financial data for {symbol}:

{context}

Provide:
1. Financial health assessment
2. Growth trends
3. Key risks
4. Investment recommendation

Be concise and data-driven.
"""

CHAT_PROMPT = """
You are a financial analyst assistant. Answer the following question:

Question: {query}

Context: {context}

Provide a clear, accurate response.
"""

FINANCIAL_CHAT_PROMPT = """
You are a financial analyst assistant specializing in stock prices, quotes, and financial metrics.
Answer the following question using the provided data:

Question: {query}

Context: {context}

Focus on specific numbers, percentages, and financial indicators. Be concise and data-driven.
"""

NEWS_CHAT_PROMPT = """
You are a financial news analyst. Answer the following question based on the latest available information:

Question: {query}

Context: {context}

Summarize key developments, their market impact, and any notable trends.
"""

RESEARCH_CHAT_PROMPT = """
You are an equity research analyst. Answer the following question with a thorough analysis:

Question: {query}

Context: {context}

Include assessment of fundamentals, risks, and any relevant investment considerations.
"""

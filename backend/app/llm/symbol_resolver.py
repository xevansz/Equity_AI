from app.llm.gemini import gemini
import re

SYMBOL_RESOLUTION_PROMPT = """
You are a financial entity resolver.

Your task is to extract the publicly traded stock ticker symbol
from a user query.

Rules:
- Return ONLY the ticker symbol.
- No explanation.
- No punctuation.
- No extra words.
- Uppercase letters only.
- If multiple companies are mentioned, return the main company.
- If no public company is found, return: UNKNOWN

Examples:

Query: "Should I invest in Apple?"
Answer: AAPL

Query: "Tesla earnings report"
Answer: TSLA

Query: "Microsoft vs Google stock"
Answer: MSFT

Query: "Tell me about gold prices"
Answer: UNKNOWN

Now resolve this:

Question: "{query}"
Answer:
"""


def normalize_symbol(raw: str) -> str:
  raw = raw.strip().upper()

  # Extract ticker symbol
  match = re.search(r"\b[A-Z]{1,6}\b", raw)
  if match:
    return match.group(0)

  return "UNKNOWN"


async def symbol_resolver(query: str):
  try:
    prompt = SYMBOL_RESOLUTION_PROMPT.format(query=query)
    response = await gemini.generate(prompt)
    return normalize_symbol(response)
  except Exception as e:
    print(f"Symbol resolution failed: {e}")
    return "UNKNOWN"

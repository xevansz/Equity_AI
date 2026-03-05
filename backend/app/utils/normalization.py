import re

_CORP_SUFFIXES = {
    "inc",
    "corp",
    "corporation",
    "company",
    "co",
    "ltd",
    "limited",
    "holdings",
    "group",
}

_PUNCTUATION_RE = re.compile(r"[^\w\s]")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_company_name(name: str) -> str:
    """Normalize a company name for alias matching.

    Steps:
    - lowercase
    - remove punctuation
    - collapse whitespace
    - remove trailing corporate suffixes
    """
    name = name.lower()
    name = _PUNCTUATION_RE.sub(" ", name)
    name = _WHITESPACE_RE.sub(" ", name).strip()

    tokens = name.split()
    while tokens and tokens[-1] in _CORP_SUFFIXES:
        tokens.pop()

    return " ".join(tokens)


_TICKER_RE = re.compile(r"^[A-Z]{1,6}$")


def looks_like_ticker(query: str) -> bool:
    """Return True if query looks like a stock ticker symbol (e.g. TSLA, AAPL)."""
    return bool(_TICKER_RE.match(query.strip().upper())) and len(query.strip().split()) == 1

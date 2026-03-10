class QueryExpander:
    def expand_query(self, query: str) -> list:
        # Generate multiple query variations
        expansions = [query, f"What are the financial metrics for {query}", f"Recent news about {query}"]
        return expansions

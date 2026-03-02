"""Data Cleaning Utilities"""

import re


class DataCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text

    @staticmethod
    def clean_financial_data(data: dict) -> dict:
        # Remove nulls, normalize keys
        return {k: v for k, v in data.items() if v is not None}


data_cleaner = DataCleaner()

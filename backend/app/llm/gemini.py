"""Gemini LLM Client"""

from google import genai

from app.config import settings


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    async def generate(self, prompt: str) -> str:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text

    async def generate_conversation(self, messages: list[dict[str, str]]) -> str:
        """Generate response using multi-turn conversation format.

        Args:
            messages: List of dicts with 'role' ('user' or 'model') and 'content'

        Returns:
            Generated response text
        """
        contents = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages]
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=contents,
        )
        return response.text


gemini = GeminiClient()

"""Response Generator"""

from app.llm.gemini import gemini
from app.llm.prompt_templates import CHAT_PROMPT


class ResponseGenerator:
    async def generate_response(self, query: str, context: str):
        prompt = CHAT_PROMPT.format(query=query, context=context)
        response = await gemini.generate(prompt)
        return response


response_generator = ResponseGenerator()

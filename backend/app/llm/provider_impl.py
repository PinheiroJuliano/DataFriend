import json
from app.config import settings
from app.llm.provider import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=settings.llm_api_key)
        self.model = settings.llm_model or "claude-3-5-sonnet-20241022"

    async def generate_sql(self, question: str, schema: str) -> str:
        from app.agent.prompts import sql_prompt
        prompt = sql_prompt(question=question, schema=schema)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def explain_result(self, question: str, sql: str, result: str) -> str:
        from app.agent.prompts import explanation_prompt
        prompt = explanation_prompt(question=question, sql=sql, result=result)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


class GeminiProvider(LLMProvider):
    def __init__(self):
        from google import genai
        self.client = genai.Client(api_key=settings.llm_api_key)
        self.model = settings.llm_model or "gemini-2.0-flash"

    async def generate_sql(self, question: str, schema: str) -> str:
        from app.agent.prompts import sql_prompt
        prompt = sql_prompt(question=question, schema=schema)
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text

    async def explain_result(self, question: str, sql: str, result: str) -> str:
        from app.agent.prompts import explanation_prompt
        prompt = explanation_prompt(question=question, sql=sql, result=result)
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "anthropic":
        return AnthropicProvider()
    if settings.llm_provider == "gemini":
        return GeminiProvider()
    raise ValueError(f"Provider não suportado: {settings.llm_provider}")

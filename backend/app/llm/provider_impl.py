import json
from app.config import settings
from app.llm.provider import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = ""):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model or "claude-3-5-sonnet-20241022"

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
    def __init__(self, api_key: str, model: str = ""):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model = model or "gemini-3.6-flash"

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


class FallbackLLMProvider(LLMProvider):
    def __init__(self, primary: LLMProvider, fallback: LLMProvider):
        self.primary = primary
        self.fallback = fallback

    async def generate_sql(self, question: str, schema: str) -> str:
        try:
            return await self.primary.generate_sql(question=question, schema=schema)
        except Exception:
            return await self.fallback.generate_sql(question=question, schema=schema)

    async def explain_result(self, question: str, sql: str, result: str) -> str:
        try:
            return await self.primary.explain_result(
                question=question,
                sql=sql,
                result=result,
            )
        except Exception:
            return await self.fallback.explain_result(
                question=question,
                sql=sql,
                result=result,
            )


def _build_provider(provider: str, api_key: str, model: str) -> LLMProvider:
    if provider == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model)
    if provider == "gemini":
        return GeminiProvider(api_key=api_key, model=model)
    raise ValueError(f"Provider não suportado: {provider}")


def get_llm_provider() -> LLMProvider:
    primary = _build_provider(
        provider=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
    )

    if not settings.llm_fallback_provider:
        return primary

    if not settings.llm_fallback_api_key:
        raise ValueError("LLM_FALLBACK_API_KEY é obrigatória quando o fallback está configurado")

    fallback = _build_provider(
        provider=settings.llm_fallback_provider,
        api_key=settings.llm_fallback_api_key,
        model=settings.llm_fallback_model,
    )
    return FallbackLLMProvider(primary=primary, fallback=fallback)

from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def generate_sql(self, question: str, schema: str) -> str:
        ...

    @abstractmethod
    async def explain_result(self, question: str, sql: str, result: str) -> str:
        ...

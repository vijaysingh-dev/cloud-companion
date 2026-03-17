import logging
from typing import Optional, Dict
from textwrap import dedent

from app.llm.provider import LLMProvider
from app.llm.prompt_registry import PromptRegistry
from app.llm.cache import LLMCache

logger = logging.getLogger(__name__)


class LLMService:

    def __init__(self):

        self.provider = LLMProvider()
        self.prompts = PromptRegistry()
        self.cache = LLMCache()

    async def generate_answer(
        self,
        user_query: str,
        context: Optional[str] = None,
    ) -> str:

        system_prompt = self.prompts.get_prompt(
            "system",
            "cloud_troubleshoot",
        )

        if context:
            system_prompt += f"\n\nContext:\n{context}"

        payload = system_prompt + user_query
        cached = self.cache.get(payload)

        if cached:
            return cached

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]

        response = await self.provider.completion(messages)

        self.cache.set(payload, response)

        return response  # type: ignore

    async def humanize_resources(
        self,
        resources: Dict,
        relationships: Dict,
    ):

        prompt = self.prompts.get_prompt(
            "small_llm",
            "humanize_resources",
        )

        payload = str(resources) + str(relationships)

        cached = self.cache.get(payload)

        if cached:
            return cached

        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": dedent(
                    f"""Resources:
                    {resources}

                    Relationships:
                    {relationships}

                    Convert into factual sentences."""
                ).strip(),
            },
        ]

        result = await self.provider.completion(messages, small=True)

        self.cache.set(payload, result)

        return result

    async def create_embedding(self, text: str):

        cached = self.cache.get(text)

        if cached:
            return cached

        embedding = await self.provider.embedding(text)

        self.cache.set(text, embedding)

        return embedding

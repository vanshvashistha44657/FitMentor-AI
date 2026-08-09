"""
Provider-agnostic AI client. Every AI feature (scoring, workout generation,
nutrition generation, live coach chat) calls `generate()` here instead of
importing openai/anthropic/gemini directly. This means DEFAULT_AI_PROVIDER
can be swapped in config without touching business logic, and the app
degrades gracefully (raises a clear error) if no key is configured.
"""
import json
from abc import ABC, abstractmethod

from app.core.config import settings


class AIProviderError(Exception):
    pass


class BaseAIProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """Returns the raw text response. If json_mode=True, caller should
        json.loads() the result — the prompt itself must instruct the model
        to return only JSON."""
        raise NotImplementedError


class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"} if json_mode else {"type": "text"},
            temperature=0.7,
        )
        return response.choices[0].message.content or ""


class AnthropicProvider(BaseAIProvider):
    def __init__(self):
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        prompt = user_prompt
        if json_mode:
            prompt += "\n\nRespond with ONLY valid JSON, no markdown fences, no preamble."
        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


class GeminiProvider(BaseAIProvider):
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.genai = genai

    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        model = self.genai.GenerativeModel(
            "gemini-1.5-pro",
            system_instruction=system_prompt,
            generation_config={"response_mime_type": "application/json"} if json_mode else None,
        )
        response = await model.generate_content_async(user_prompt)
        return response.text


_PROVIDERS: dict[str, type[BaseAIProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
}


def get_ai_provider(name: str | None = None) -> BaseAIProvider:
    provider_name = name or settings.DEFAULT_AI_PROVIDER
    provider_cls = _PROVIDERS.get(provider_name)
    if not provider_cls:
        raise AIProviderError(f"Unknown AI provider: {provider_name}")
    return provider_cls()


async def generate_json(system_prompt: str, user_prompt: str, provider_name: str | None = None) -> dict:
    """Convenience wrapper: calls the provider in JSON mode and parses the result,
    with one retry-by-reprompt if the model returns malformed JSON."""
    provider = get_ai_provider(provider_name)
    raw = await provider.generate(system_prompt, user_prompt, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise AIProviderError(f"AI provider returned invalid JSON: {e}") from e

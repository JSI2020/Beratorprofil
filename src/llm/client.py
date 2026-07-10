"""Unified LLM client for OpenAI-compatible providers (DeepSeek, Mistral, OpenAI)."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    api_key: str
    base_url: str | None
    model: str


PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "key_env": "DEEPSEEK_API_KEY",
        "model_env": "DEEPSEEK_MODEL",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "model": "mistral-large-latest",
        "key_env": "MISTRAL_API_KEY",
        "model_env": "MISTRAL_MODEL",
    },
    "openai": {
        "base_url": "",
        "model": "gpt-4o",
        "key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
    },
}


def llm_available() -> bool:
    return resolve_llm_config() is not None


def resolve_llm_config() -> LLMConfig | None:
    explicit = os.getenv("LLM_PROVIDER", "").strip().lower()
    if explicit:
        return _config_for_provider(explicit)

    for provider in ("deepseek", "mistral", "openai"):
        config = _config_for_provider(provider)
        if config:
            return config

    if os.getenv("ANTHROPIC_API_KEY"):
        return LLMConfig(
            provider="anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            base_url=None,
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        )
    return None


def _config_for_provider(provider: str) -> LLMConfig | None:
    defaults = PROVIDER_DEFAULTS.get(provider)
    if not defaults:
        return None

    api_key = os.getenv(defaults["key_env"], "").strip()
    if not api_key:
        return None

    base_url = os.getenv(f"{provider.upper()}_BASE_URL", defaults["base_url"]).strip() or None
    model = os.getenv(defaults["model_env"], defaults["model"]).strip()
    return LLMConfig(provider=provider, api_key=api_key, base_url=base_url, model=model)


def call_llm_json(system_prompt: str, user_payload: dict) -> dict:
    config = resolve_llm_config()
    if not config:
        raise RuntimeError(
            "No LLM API key configured. Set DEEPSEEK_API_KEY or MISTRAL_API_KEY in .env"
        )

    user_content = json.dumps(user_payload, ensure_ascii=False)

    if config.provider == "anthropic":
        return _call_anthropic(config, system_prompt, user_content)

    return _call_openai_compatible(config, system_prompt, user_content)


def _call_openai_compatible(config: LLMConfig, system_prompt: str, user_content: str) -> dict:
    from openai import OpenAI

    client_kwargs: dict = {"api_key": config.api_key}
    if config.base_url:
        client_kwargs["base_url"] = config.base_url

    client = OpenAI(**client_kwargs)
    response = client.chat.completions.create(
        model=config.model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )
    return _parse_json_response(response.choices[0].message.content or "")


def _call_anthropic(config: LLMConfig, system_prompt: str, user_content: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=config.api_key)
    response = client.messages.create(
        model=config.model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return _parse_json_response(response.content[0].text)


def _parse_json_response(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)

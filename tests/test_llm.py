"""Tests for LLM provider configuration."""

import os

from src.llm.client import llm_available, resolve_llm_config


def test_deepseek_config(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")

    config = resolve_llm_config()
    assert config is not None
    assert config.provider == "deepseek"
    assert config.model == "deepseek-chat"
    assert llm_available() is True


def test_mistral_config_when_provider_set(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mistral")
    monkeypatch.setenv("MISTRAL_API_KEY", "test-mistral-key")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    config = resolve_llm_config()
    assert config is not None
    assert config.provider == "mistral"
    assert config.base_url == "https://api.mistral.ai/v1"

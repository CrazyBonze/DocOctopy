"""Configuration for canned integration tests."""

import os
from pathlib import Path

# Base directory for canned tests
BASE_DIR = Path(__file__).parent

# LLM Provider Configurations
LLM_CONFIGS = {
    "ollama": {
        "provider": "ollama",
        "base_url": "http://192.168.0.132:11434",
        "models": {
            "codeqwen": "codeqwen:latest",
            "llama": "llama3.1:8b",
            "codellama": "codellama:7b",
        },
    },
    "openai": {
        "provider": "openai",
        "api_key_env": "OPENAI_API_KEY",
        "models": {
            "gpt4_mini": "gpt-4o-mini",
            "gpt4": "gpt-4o",
            "gpt35": "gpt-3.5-turbo",
        },
    },
    "anthropic": {
        "provider": "anthropic",
        "api_key_env": "ANTHROPIC_API_KEY",
        "models": {
            "haiku": "claude-3-haiku-20240307",
            "sonnet": "claude-3-sonnet-20240229",
            "opus": "claude-3-opus-20240229",
        },
    },
}

# Test Scenarios Configuration
SCENARIOS = {
    "missing_docstrings": {
        "description": "Add docstrings to functions and classes without them",
        "fixture": "missing_docstrings.py",
        "rules": ["DG101"],
        "expected_changes": 6,
    },
    "malformed_docstrings": {
        "description": "Fix malformed Google-style docstrings",
        "fixture": "malformed_docstrings.py",
        "rules": ["DG201", "DG202", "DG203", "DG204"],
        "expected_changes": 5,
    },
    "mixed_issues": {
        "description": "Handle mixed docstring issues",
        "fixture": "mixed_issues.py",
        "rules": ["DG101", "DG202", "DG204", "DG205"],
        "expected_changes": 8,
    },
    "real_world_patterns": {
        "description": "Real-world code patterns from actual projects",
        "fixture": "real_world_patterns.py",
        "rules": ["DG101", "DG202", "DG204"],
        "expected_changes": 10,
    },
}

# Default test configurations
DEFAULT_CONFIGS = [
    {
        "name": "ollama_codeqwen",
        "provider": "ollama",
        "model": "codeqwen:latest",
        "base_url": "http://192.168.0.132:11434",
    },
    {
        "name": "openai_gpt4_mini",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "requires_api_key": True,
    },
    {
        "name": "anthropic_haiku",
        "provider": "anthropic",
        "model": "claude-3-haiku-20240307",
        "requires_api_key": True,
    },
]


def get_api_key(provider: str) -> str:
    """Get API key for provider from environment."""
    config = LLM_CONFIGS.get(provider)
    if not config or "api_key_env" not in config:
        return ""

    return os.getenv(config["api_key_env"], "")


def check_api_key_available(provider: str) -> bool:
    """Check if API key is available for provider."""
    return bool(get_api_key(provider))


def get_available_configs():
    """Get list of available configurations based on API keys."""
    available = []

    for config in DEFAULT_CONFIGS:
        provider = config["provider"]

        # Check if API key is required and available
        if config.get("requires_api_key", False):
            if not check_api_key_available(provider):
                continue

        available.append(config)

    return available

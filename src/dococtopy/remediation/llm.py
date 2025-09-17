"""LLM client abstraction using DSPy for docstring generation.

This module provides a unified interface for different LLM providers
using DSPy's model-agnostic approach.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    import dspy
except ImportError:
    dspy = None  # type: ignore


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""

    provider: str  # "openai", "anthropic", "ollama", etc.
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1  # Low temperature for consistent docstring generation
    max_tokens: int = 1000


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_docstring(
        self,
        function_signature: str,
        function_purpose: str,
        existing_docstring: str = "",
        context: str = "",
    ) -> str:
        """Generate a docstring for a function or class."""
        pass

    @abstractmethod
    def fix_docstring(
        self,
        function_signature: str,
        current_docstring: str,
        issues: str,
    ) -> str:
        """Fix a non-compliant docstring."""
        pass

    @abstractmethod
    def enhance_docstring(
        self,
        function_signature: str,
        current_docstring: str,
        missing_elements: str,
    ) -> str:
        """Enhance an existing docstring with missing information."""
        pass


class DSPyLLMClient(LLMClient):
    """DSPy-based LLM client for docstring generation."""

    def __init__(self, config: LLMConfig):
        if dspy is None:
            raise ImportError(
                "DSPy is required for LLM functionality. Install with: pip install dspy-ai"
            )

        self.config = config
        self._setup_lm()
        self._setup_modules()

    def _setup_lm(self) -> None:
        """Set up the language model based on configuration."""
        if self.config.provider == "openai":
            api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key."
                )

            self.lm = dspy.LM(  # type: ignore
                model=self.config.model,
                api_key=api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
        elif self.config.provider == "anthropic":
            api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable or pass api_key."
                )

            self.lm = dspy.LM(  # type: ignore
                model=self.config.model,
                api_key=api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
        elif self.config.provider == "ollama":
            # Use litellm for Ollama support
            import litellm

            # Configure litellm for Ollama
            litellm.api_base = self.config.base_url or "http://localhost:11434"

            self.lm = dspy.LM(  # type: ignore
                model=f"ollama/{self.config.model}",
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        # Set as default LM for DSPy
        dspy.settings.configure(lm=self.lm)  # type: ignore

    def _setup_modules(self) -> None:
        """Set up DSPy modules for different docstring tasks."""
        from .signatures import DocstringEnhancement, DocstringFix, DocstringGeneration

        self.generate_module = dspy.Predict(DocstringGeneration)  # type: ignore
        self.fix_module = dspy.Predict(DocstringFix)  # type: ignore
        self.enhance_module = dspy.Predict(DocstringEnhancement)  # type: ignore

    def generate_docstring(
        self,
        function_signature: str,
        function_purpose: str,
        existing_docstring: str = "",
        context: str = "",
    ) -> str:
        """Generate a docstring for a function or class."""
        try:
            result = self.generate_module(
                function_signature=function_signature,
                function_purpose=function_purpose,
                existing_docstring=existing_docstring,
                context=context,
            )
            return result.docstring
        except Exception as e:
            raise RuntimeError(f"Failed to generate docstring: {e}")

    def fix_docstring(
        self,
        function_signature: str,
        current_docstring: str,
        issues: str,
    ) -> str:
        """Fix a non-compliant docstring."""
        try:
            result = self.fix_module(
                function_signature=function_signature,
                current_docstring=current_docstring,
                issues=issues,
            )
            return result.fixed_docstring
        except Exception as e:
            raise RuntimeError(f"Failed to fix docstring: {e}")

    def enhance_docstring(
        self,
        function_signature: str,
        current_docstring: str,
        missing_elements: str,
    ) -> str:
        """Enhance an existing docstring with missing information."""
        try:
            result = self.enhance_module(
                function_signature=function_signature,
                current_docstring=current_docstring,
                missing_elements=missing_elements,
            )
            return result.enhanced_docstring
        except Exception as e:
            raise RuntimeError(f"Failed to enhance docstring: {e}")


def create_llm_client(config: LLMConfig) -> LLMClient:
    """Factory function to create an LLM client."""
    return DSPyLLMClient(config)


def get_default_config() -> LLMConfig:
    """Get default LLM configuration based on environment."""
    # Check for available API keys
    if os.getenv("OPENAI_API_KEY"):
        return LLMConfig(
            provider="openai",
            model="gpt-4o-mini",  # Cost-effective model for docstring generation
        )
    elif os.getenv("ANTHROPIC_API_KEY"):
        return LLMConfig(
            provider="anthropic",
            model="claude-3-haiku-20240307",  # Fast and cost-effective
        )
    else:
        # Default to local Ollama if no API keys found
        return LLMConfig(
            provider="ollama",
            model="llama3.1:8b",  # Good balance of quality and speed
        )


def get_recommended_models() -> Dict[str, List[str]]:
    """Get recommended models for different use cases."""
    return {
        "free_tier": [
            "gpt-4o-mini",  # OpenAI free tier
            "claude-3-haiku-20240307",  # Anthropic free tier
            "llama3.1:8b",  # Local Ollama
        ],
        "fast": [
            "gpt-4o-mini",
            "claude-3-haiku-20240307",
            "llama3.1:8b",
        ],
        "high_quality": [
            "gpt-4o",
            "claude-3-sonnet-20240229",
            "llama3.1:70b",
        ],
        "local_only": [
            "llama3.1:8b",
            "llama3.1:70b",
            "codellama:7b",
            "codellama:13b",
        ],
    }

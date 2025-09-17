"""Configuration management for canned integration tests."""

import os
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt


class CannedTestConfig:
    """Configuration for canned tests with environment variable support."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path.home() / ".dococtopy_test_config"
        self.console = Console()
        self._config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                import json

                with open(self.config_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                self.console.print(
                    f"[yellow]Warning: Could not load config from {self.config_file}[/yellow]"
                )

        return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Get default configuration with environment variable fallbacks."""
        return {
            "ollama": {
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "default_model": os.getenv("OLLAMA_MODEL", "codeqwen:latest"),
                "models": {
                    "codeqwen": os.getenv("OLLAMA_CODEQWEN_MODEL", "codeqwen:latest"),
                    "llama": os.getenv("OLLAMA_LLAMA_MODEL", "llama3.1:8b"),
                    "codellama": os.getenv("OLLAMA_CODELLAMA_MODEL", "codellama:7b"),
                },
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "default_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "models": {
                    "gpt4_mini": os.getenv("OPENAI_GPT4_MINI_MODEL", "gpt-4o-mini"),
                    "gpt4": os.getenv("OPENAI_GPT4_MODEL", "gpt-4o"),
                    "gpt35": os.getenv("OPENAI_GPT35_MODEL", "gpt-3.5-turbo"),
                },
            },
            "anthropic": {
                "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                "default_model": os.getenv(
                    "ANTHROPIC_MODEL", "claude-3-haiku-20240307"
                ),
                "models": {
                    "haiku": os.getenv(
                        "ANTHROPIC_HAIKU_MODEL", "claude-3-haiku-20240307"
                    ),
                    "sonnet": os.getenv(
                        "ANTHROPIC_SONNET_MODEL", "claude-3-sonnet-20240229"
                    ),
                    "opus": os.getenv("ANTHROPIC_OPUS_MODEL", "claude-3-opus-20240229"),
                },
            },
        }

    def save_config(self):
        """Save current configuration to file."""
        try:
            import json

            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
            self.console.print(
                f"[green]Configuration saved to {self.config_file}[/green]"
            )
        except IOError as e:
            self.console.print(f"[red]Error saving config: {e}[/red]")

    def get_ollama_config(self) -> Dict:
        """Get Ollama configuration."""
        return self._config["ollama"]

    def get_openai_config(self) -> Dict:
        """Get OpenAI configuration."""
        return self._config["openai"]

    def get_anthropic_config(self) -> Dict:
        """Get Anthropic configuration."""
        return self._config["anthropic"]

    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is properly configured."""
        if provider == "ollama":
            return True  # Ollama doesn't require API key
        elif provider == "openai":
            return bool(self._config["openai"]["api_key"])
        elif provider == "anthropic":
            return bool(self._config["anthropic"]["api_key"])
        return False

    def interactive_setup(self):
        """Interactive configuration setup."""
        self.console.print("[bold blue]DocOctopy Test Configuration Setup[/bold blue]")
        self.console.print(
            "This will help you configure LLM providers for canned tests.\n"
        )

        # Ollama configuration
        self.console.print("[bold]Ollama Configuration[/bold]")
        ollama_url = Prompt.ask(
            "Ollama base URL", default=self._config["ollama"]["base_url"]
        )
        ollama_model = Prompt.ask(
            "Default Ollama model", default=self._config["ollama"]["default_model"]
        )

        self._config["ollama"]["base_url"] = ollama_url
        self._config["ollama"]["default_model"] = ollama_model

        # OpenAI configuration
        self.console.print("\n[bold]OpenAI Configuration[/bold]")
        if Confirm.ask("Configure OpenAI?", default=False):
            openai_key = Prompt.ask("OpenAI API Key", password=True)
            openai_model = Prompt.ask(
                "Default OpenAI model", default=self._config["openai"]["default_model"]
            )

            self._config["openai"]["api_key"] = openai_key
            self._config["openai"]["default_model"] = openai_model

        # Anthropic configuration
        self.console.print("\n[bold]Anthropic Configuration[/bold]")
        if Confirm.ask("Configure Anthropic?", default=False):
            anthropic_key = Prompt.ask("Anthropic API Key", password=True)
            anthropic_model = Prompt.ask(
                "Default Anthropic model",
                default=self._config["anthropic"]["default_model"],
            )

            self._config["anthropic"]["api_key"] = anthropic_key
            self._config["anthropic"]["default_model"] = anthropic_model

        # Save configuration
        if Confirm.ask("\nSave configuration?", default=True):
            self.save_config()

    def show_config(self):
        """Display current configuration (hiding sensitive data)."""
        self.console.print("[bold blue]Current Test Configuration[/bold blue]\n")

        # Ollama
        ollama = self._config["ollama"]
        self.console.print(f"[bold]Ollama:[/bold]")
        self.console.print(f"  Base URL: {ollama['base_url']}")
        self.console.print(f"  Default Model: {ollama['default_model']}")

        # OpenAI
        openai = self._config["openai"]
        self.console.print(f"\n[bold]OpenAI:[/bold]")
        if openai["api_key"]:
            self.console.print(f"  API Key: {'*' * 20}...{openai['api_key'][-4:]}")
        else:
            self.console.print(f"  API Key: [red]Not configured[/red]")
        self.console.print(f"  Default Model: {openai['default_model']}")

        # Anthropic
        anthropic = self._config["anthropic"]
        self.console.print(f"\n[bold]Anthropic:[/bold]")
        if anthropic["api_key"]:
            self.console.print(f"  API Key: {'*' * 20}...{anthropic['api_key'][-4:]}")
        else:
            self.console.print(f"  API Key: [red]Not configured[/red]")
        self.console.print(f"  Default Model: {anthropic['default_model']}")

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        available = []
        if self.is_provider_available("ollama"):
            available.append("ollama")
        if self.is_provider_available("openai"):
            available.append("openai")
        if self.is_provider_available("anthropic"):
            available.append("anthropic")
        return available


# Global config instance
_config_instance: Optional[CannedTestConfig] = None


def get_config() -> CannedTestConfig:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = CannedTestConfig()
    return _config_instance


def setup_config():
    """Interactive configuration setup."""
    config = get_config()
    config.interactive_setup()


def show_config():
    """Show current configuration."""
    config = get_config()
    config.show_config()

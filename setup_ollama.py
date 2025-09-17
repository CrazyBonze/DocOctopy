#!/usr/bin/env python3
"""Quick setup script for Ollama configuration."""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.canned.test_config import get_config


def setup_ollama():
    """Set up Ollama configuration."""
    config = get_config()

    # Set your Ollama configuration
    config._config["ollama"]["base_url"] = "http://192.168.0.132:11434"
    config._config["ollama"]["default_model"] = "codeqwen:latest"

    # Save configuration
    config.save_config()
    print("✅ Ollama configuration saved!")
    print(f"   Base URL: {config._config['ollama']['base_url']}")
    print(f"   Model: {config._config['ollama']['default_model']}")


if __name__ == "__main__":
    setup_ollama()

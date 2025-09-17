#!/usr/bin/env python3
"""Quick setup script for OpenAI configuration."""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.canned.test_config import get_config


def setup_openai():
    """Set up OpenAI configuration."""
    config = get_config()

    # Get API key from user
    api_key = input("Enter your OpenAI API key: ").strip()
    if not api_key:
        print("❌ No API key provided")
        return

    # Set OpenAI configuration
    config._config["openai"]["api_key"] = api_key
    config._config["openai"]["default_model"] = "gpt-4o-mini"

    # Save configuration
    config.save_config()
    print("✅ OpenAI configuration saved!")
    print(f"   Model: {config._config['openai']['default_model']}")
    print(f"   API Key: {'*' * 20}...{api_key[-4:]}")


if __name__ == "__main__":
    setup_openai()

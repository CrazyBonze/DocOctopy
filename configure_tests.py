#!/usr/bin/env python3
"""Configuration script for DocOctopy canned tests."""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.canned.test_config import setup_config, show_config

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Configure DocOctopy canned tests")
    parser.add_argument(
        "--show", action="store_true", help="Show current configuration"
    )
    parser.add_argument("--setup", action="store_true", help="Setup configuration")

    args = parser.parse_args()

    if args.show:
        show_config()
    elif args.setup:
        setup_config()
    else:
        parser.print_help()

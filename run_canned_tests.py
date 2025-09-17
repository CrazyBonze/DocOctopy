#!/usr/bin/env python3
"""Simple script to run DocOctopy canned integration tests."""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.canned.test_runner import main

if __name__ == "__main__":
    main()

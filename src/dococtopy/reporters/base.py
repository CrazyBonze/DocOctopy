"""
Base reporter interface for output formatting.

This module defines the base interface for output reporters.
Reporters handle formatting scan results into various output formats.

Available reporters:
- Console reporter (pretty output)
- JSON reporter (machine-readable)
- SARIF reporter (GitHub Code Scanning)

Planned reporters:
- HTML reporter
- Markdown reporter
- CSV reporter
- Custom format support
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

# TODO: Define base reporter interface
# TODO: Add HTML reporter
# TODO: Add Markdown reporter
# TODO: Add CSV reporter
# TODO: Add custom format support

"""
Base rule interface for compliance checking.

This module defines the base interface for compliance rules.
Rules are used to check code for various documentation compliance issues.

Current rule types:
- Basic compliance rules (DG101, DG301, DG302)
- Google style validation rules (DG201-DG210)
- Advanced Google style rules (DG211-DG214)

Planned rule types:
- Coverage threshold rules
- Custom rule framework
- Language-specific rules
"""

from abc import ABC, abstractmethod
from typing import List, Optional

# TODO: Define base rule interface
# TODO: Add rule severity levels
# TODO: Add rule configuration framework
# TODO: Add custom rule support

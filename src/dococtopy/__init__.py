"""
DocOctopy - A language-agnostic docstyle compliance & remediation tool.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A language-agnostic docstyle compliance & remediation tool"

# Core exports
from dococtopy.core.findings import Finding, FindingLevel

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "Finding",
    "FindingLevel",
]

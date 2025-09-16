"""Simple rule registry for MVP."""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Protocol

from dococtopy.core.findings import Finding


class Rule(Protocol):
    id: str
    name: str
    level_default: str

    def check(self, *, symbols) -> List[Finding]:  # pragma: no cover - protocol
        ...


_REGISTRY: Dict[str, Rule] = {}


def register(rule: Rule) -> None:
    if rule.id in _REGISTRY:
        raise ValueError(f"Duplicate rule id {rule.id}")
    _REGISTRY[rule.id] = rule


def all_rules() -> Iterable[Rule]:
    return _REGISTRY.values()


def get_rule(rule_id: str) -> Rule:
    return _REGISTRY[rule_id]

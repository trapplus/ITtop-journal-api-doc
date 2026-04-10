"""Recursive anonymization of JSON-like payloads."""

from typing import Any

from src.anonymizer.rules import RULES


class Anonymizer:
    """Replace configured fields with synthetic values."""

    def anonymize(self, data: dict | list) -> dict | list:
        """Return a new anonymized copy of a dict/list payload."""

        return self._anonymize_node(data)

    def _anonymize_node(self, node: Any) -> Any:
        """Recursively process nested structures and apply replacement rules."""

        if isinstance(node, dict):
            anonymized: dict[str, Any] = {}
            for key, value in node.items():
                lowered_key = key.lower()
                if lowered_key in RULES:
                    anonymized[key] = RULES[lowered_key]()
                elif isinstance(value, (dict, list)):
                    anonymized[key] = self._anonymize_node(value)
                else:
                    anonymized[key] = value
            return anonymized

        if isinstance(node, list):
            return [self._anonymize_node(item) if isinstance(item, (dict, list)) else item for item in node]

        return node

"""Validation runner for endpoint response payloads."""

import logging
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from src.validator.models import MODELS

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ValidationResult:
    """Validation status for a single endpoint."""

    endpoint: str
    success: bool
    errors: list[str]


class Validator:
    """Validate raw endpoint payloads against configured Pydantic models."""

    def validate_all(self, raw: dict[str, Any]) -> list[ValidationResult]:
        """Validate each collected endpoint response."""

        results: list[ValidationResult] = []

        for endpoint, data in raw.items():
            model = MODELS.get(endpoint)
            if model is None:
                LOGGER.warning("No model registered for endpoint %s; skipping.", endpoint)
                results.append(ValidationResult(endpoint=endpoint, success=True, errors=[]))
                continue

            if isinstance(data, dict) and "error" in data:
                results.append(
                    ValidationResult(
                        endpoint=endpoint,
                        success=False,
                        errors=[f"Collection error: {data['error']}"],
                    )
                )
                continue

            try:
                model.model_validate(data)
                results.append(ValidationResult(endpoint=endpoint, success=True, errors=[]))
            except ValidationError as error:
                errors = [self._format_error_item(item) for item in error.errors()]
                results.append(ValidationResult(endpoint=endpoint, success=False, errors=errors))

        return results

    def has_failures(self, results: list[ValidationResult]) -> bool:
        """Return True if at least one endpoint validation failed."""

        return any(not result.success for result in results)

    def format_issue_body(self, results: list[ValidationResult]) -> str:
        """Build markdown report for validation failures."""

        failed = [result for result in results if not result.success]

        lines = [
            "# API schema changed - validation failed",
            "",
            "Collected payloads do not match current validation models.",
            "",
        ]

        if not failed:
            lines.append("No validation failures detected.")
            return "\n".join(lines) + "\n"

        for result in failed:
            lines.append(f"## `{result.endpoint}`")
            for error in result.errors:
                lines.append(f"- {error}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _format_error_item(error: dict[str, Any]) -> str:
        """Convert Pydantic error dict into readable markdown bullet text."""

        location = ".".join(str(part) for part in error.get("loc", ("<root>",)))
        message = error.get("msg", "Unknown validation error")
        return f"{location}: {message}"

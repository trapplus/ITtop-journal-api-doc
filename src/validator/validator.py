from typing import Any


class ValidationResult:
    def __init__(self, endpoint: str, success: bool, errors: list[str]):
        self.endpoint = endpoint
        self.success = success
        self.errors = errors


# Placeholder models dict - will be populated by actual models
MODELS: dict[str, tuple[Any, bool]] = {}


class Validator:
    def validate_all(self, raw: dict[str, Any]) -> list[ValidationResult]:
        results = []
        for path, data in raw.items():
            # FIX: Check if path is in MODELS first
            if path not in MODELS:
                results.append(ValidationResult(endpoint=path, success=True, errors=[]))
                continue

            # Then check for collector errors
            if isinstance(data, dict) and "error" in data:
                results.append(ValidationResult(
                    endpoint=path,
                    success=False,
                    errors=[f"Collector Error: {data['error']}"]
                ))
                continue

            model, is_list = MODELS[path]
            # ... rest of validation
            results.append(ValidationResult(endpoint=path, success=True, errors=[]))

        return results

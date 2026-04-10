"""OpenAPI specification builder for collected Journal endpoint data."""

import json
from datetime import date
from pathlib import Path
from typing import Any

from src.collector.endpoints import ENDPOINTS

API_DOWN_WARNING = "⚠️ API unavailable at collection time. Examples may be outdated."


class OpenAPIBuilder:
    """Build and persist OpenAPI schema generated from known endpoints."""

    def build(self, examples: dict[str, Any], is_api_down: bool = False) -> dict:
        """Build OpenAPI 3.0.3 document with examples from collected payloads."""

        description = "Auto-generated documentation from daily Journal API collection."
        if is_api_down:
            description = f"{description}\n\n{API_DOWN_WARNING}"

        spec: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": {
                "title": "IT Top Journal API",
                "version": date.today().isoformat(),
                "description": description,
            },
            "paths": {},
        }

        for endpoint in ENDPOINTS:
            method = endpoint.method.lower()
            operation: dict[str, Any] = {
                "summary": f"{endpoint.method} {endpoint.path}",
                "description": f"Auto-generated operation for `{endpoint.path}`.",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "additionalProperties": True,
                                }
                            }
                        },
                    }
                },
            }

            if endpoint.method.upper() == "GET" and endpoint.params:
                operation["parameters"] = [
                    {
                        "name": key,
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                        "example": value,
                    }
                    for key, value in endpoint.params.items()
                ]

            if endpoint.method.upper() == "POST" and endpoint.params:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object", "additionalProperties": True},
                            "example": endpoint.params,
                        }
                    },
                }

            if endpoint.path in examples:
                operation["responses"]["200"]["content"]["application/json"]["example"] = examples[
                    endpoint.path
                ]

            spec["paths"].setdefault(endpoint.path, {})[method] = operation

        return spec

    def save(self, spec: dict, path: str = "documentation/openapi.json") -> None:
        """Persist generated OpenAPI document as formatted JSON."""

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

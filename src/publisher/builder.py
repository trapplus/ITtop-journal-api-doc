"""OpenAPI specification builder for collected Journal endpoint data."""

import json
from datetime import date
from pathlib import Path
from typing import Any

from src.collector.endpoints import ENDPOINTS, LOGIN_PATH

API_DOWN_WARNING = "⚠️ API unavailable at collection time. Examples may be outdated."
REQUIRED_HEADERS = [
    {
        "name": "Origin",
        "in": "header",
        "required": True,
        "schema": {"type": "string"},
        "example": "https://journal.top-academy.ru",
        "description": "Required by the API CORS policy.",
    },
    {
        "name": "Referer",
        "in": "header",
        "required": True,
        "schema": {"type": "string"},
        "example": "https://journal.top-academy.ru/",
        "description": "Required by the API. Must end with trailing slash.",
    },
    {
        "name": "User-Agent",
        "in": "header",
        "required": False,
        "schema": {"type": "string"},
        "example": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        ),
        "description": "Recommended to match a real browser UA to avoid blocks.",
    },
]


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
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": (
                            "JWT access token obtained from POST /auth/login response field "
                            "`access_token`. Pass as: Authorization: Bearer <token>"
                        ),
                    }
                }
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
                    "description": "Content-Type: application/json must be set explicitly.",
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object", "additionalProperties": True},
                            "example": endpoint.params,
                        }
                    },
                }

            if endpoint.path != LOGIN_PATH:
                operation["security"] = [{"BearerAuth": []}]
                existing_params = operation.get("parameters", [])
                operation["parameters"] = REQUIRED_HEADERS + existing_params

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

"""OpenAPI specification builder for collected Journal endpoint data."""

import json
from datetime import date
from pathlib import Path
from typing import Any

from src.collector.endpoints import ENDPOINTS, LOGIN_PATH
from src.validator.validator import MODELS as VALIDATOR_MODELS

API_DOWN_WARNING = "⚠️ API unavailable at collection time. Examples may be outdated."

# Обязательные заголовки для всех аутентифицированных запросов к Journal API.
# Origin и Referer проверяются сервером как часть CORS-политики —
# без них запрос вернёт 403 даже с валидным Bearer токеном.
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

# Worker — единственная точка входа для Swagger UI.
# Прямой доступ к msapi.top-academy.ru из браузера невозможен из-за CORS:
# сервер не возвращает Access-Control-Allow-Origin, браузер блокирует ответ.
#
# Worker решает это прозрачно:
#   с Bearer токеном → проксирует на реальный API (живые данные)
#   без токена       → отдаёт mock (анонимизированные данные)
SERVERS = [
    {
        "url": "https://ittop-mock.blazer19092008.workers.dev/api/v2",
        "description": "Mock + proxy: без токена — mock-данные, с Bearer токеном — реальный API",
    },
]


class OpenAPIBuilder:
    """Build and persist OpenAPI schema generated from known endpoints."""

    def build(self, examples: dict[str, Any], is_api_down: bool = False) -> dict:
        """Build OpenAPI 3.0.3 document with examples from collected payloads.

        Args:
            examples: Анонимизированные ответы эндпоинтов из anonymizer-а.
                      Ключ — путь эндпоинта (/dashboard/chart/attendance),
                      значение — уже очищенный JSON (dict или list).
            is_api_down: Если True — добавляет предупреждение в description,
                         что сбор данных не удался и примеры могут быть устаревшими.

        Returns:
            Готовый OpenAPI 3.0.3 документ в виде dict, готовый к json.dumps().
        """

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
            "servers": SERVERS,
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

            # Определяем схему ответа через реестр MODELS из validator-а.
            # is_list=True  → schema type: array  (большинство эндпоинтов)
            # is_list=False → schema type: object (например /settings/user-info)
            # Если эндпоинт не в MODELS — fallback на object, не падаем.
            if endpoint.path in VALIDATOR_MODELS:
                _model, is_list = VALIDATOR_MODELS[endpoint.path]
                if is_list:
                    response_schema = {
                        "type": "array",
                        "items": {"type": "object", "additionalProperties": True},
                    }
                else:
                    response_schema = {"type": "object", "additionalProperties": True}
            else:
                response_schema = {"type": "object", "additionalProperties": True}

            operation: dict[str, Any] = {
                "summary": f"{endpoint.method} {endpoint.path}",
                "description": f"Auto-generated operation for `{endpoint.path}`.",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": response_schema
                            }
                        },
                    }
                },
            }

            # Query-параметры для GET-эндпоинтов (например date_filter, language).
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

            # requestBody для POST-эндпоинтов (только /auth/login).
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

            # Все эндпоинты кроме /auth/login требуют Bearer токен.
            # Worker пробрасывает его на реальный API автоматически.
            # Origin/Referer/User-Agent Worker тоже подставляет сам —
            # но документируем их чтобы юзер понимал что реальный API требует.
            if endpoint.path != LOGIN_PATH:
                operation["security"] = [{"BearerAuth": []}]
                existing_params = operation.get("parameters", [])
                operation["parameters"] = REQUIRED_HEADERS + existing_params

            # Подставляем анонимизированный пример ответа если он есть.
            if endpoint.path in examples:
                operation["responses"]["200"]["content"]["application/json"]["example"] = examples[
                    endpoint.path
                ]

            spec["paths"].setdefault(endpoint.path, {})[method] = operation

        return spec

    def save(self, spec: dict, path: str = "documentation/openapi.json") -> None:
        """Persist generated OpenAPI document as formatted JSON.

        Args:
            spec: Документ из метода build().
            path: Куда сохранять. По умолчанию — папка documentation/,
                  которую деплоит GitHub Pages.
        """

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
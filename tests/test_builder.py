"""Tests for OpenAPI builder output structure."""

from src.collector.endpoints import ENDPOINTS
from src.publisher.builder import OpenAPIBuilder


def test_build_returns_required_keys():
    """Builder should produce base OpenAPI sections."""

    spec = OpenAPIBuilder().build(examples={})

    assert isinstance(spec, dict)
    assert "openapi" in spec
    assert "info" in spec
    assert "paths" in spec


def test_build_adds_api_down_warning():
    """Builder should append warning text when API was unavailable."""

    spec = OpenAPIBuilder().build(examples={}, is_api_down=True)

    assert "API unavailable at collection time" in spec["info"]["description"]


def test_build_contains_known_endpoints():
    """Builder should include all known endpoint paths and methods."""

    spec = OpenAPIBuilder().build(examples={})

    for endpoint in ENDPOINTS:
        assert endpoint.path in spec["paths"]
        assert endpoint.method.lower() in spec["paths"][endpoint.path]


def test_build_adds_security_headers_and_auth_scheme():
    """Authenticated operations should declare auth scheme."""

    spec = OpenAPIBuilder().build(examples={})
    auth_operation = spec["paths"]["/settings/user-info"]["get"]

    assert spec["components"]["securitySchemes"]["BearerAuth"]["scheme"] == "bearer"
    assert auth_operation["security"] == [{"BearerAuth": []}]


def test_build_adds_required_headers_to_authenticated_operations():
    """Authenticated operations should declare required request headers."""

    spec = OpenAPIBuilder().build(examples={})
    auth_operation = spec["paths"]["/settings/user-info"]["get"]

    assert [item["name"] for item in auth_operation["parameters"][:3]] == [
        "Origin",
        "Referer",
        "User-Agent",
    ]


def test_build_uses_username_field_for_login_example():
    """Login request example should document the real username field."""

    spec = OpenAPIBuilder().build(examples={})
    login_example = spec["paths"]["/auth/login"]["post"]["requestBody"]["content"][
        "application/json"
    ]["example"]

    assert "username" in login_example
    assert "login" not in login_example


def test_build_uses_array_schema_and_response_examples_for_list_endpoints():
    """List endpoints should expose array schemas and include collected examples."""

    examples = {"/dashboard/chart/attendance": [{"date": "2026-04-18", "value": 1}]}
    spec = OpenAPIBuilder().build(examples=examples)
    response = spec["paths"]["/dashboard/chart/attendance"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]

    assert response["schema"]["type"] == "array"
    assert response["example"] == examples["/dashboard/chart/attendance"]


def test_build_contains_official_and_mock_servers():
    """Spec should list both the real API and the mock server.

    Swagger UI показывает первый сервер по умолчанию — официальный идёт первым,
    чтобы можно было сразу делать запросы к реальному API с Bearer токеном.
    Mock остаётся вторым — для проверки структуры без авторизации.
    """

    spec = OpenAPIBuilder().build(examples={})
    urls = [s["url"] for s in spec["servers"]]

    assert "https://msapi.top-academy.ru/api/v2" in urls
    assert "https://ittop-mock.blazer19092008.workers.dev/api/v2" in urls
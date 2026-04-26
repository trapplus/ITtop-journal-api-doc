# OpenAPI Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich the generated OpenAPI document so it reflects the current auth payload, bearer authentication, required headers, and array-vs-object response shapes.

**Architecture:** Keep the generator logic in `src/publisher/builder.py` as the single source of truth for OpenAPI decoration, while `src/collector/endpoints.py` remains the source of request examples. Reuse the validator `MODELS` dispatch map to infer whether each endpoint returns an object or an array without introducing another schema registry.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, ruff

---

### Task 1: Add failing builder coverage for OpenAPI enrichment

**Files:**
- Modify: `tests/test_builder.py`
- Read: `src/publisher/builder.py`
- Read: `src/collector/endpoints.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_build_adds_security_headers_and_auth_scheme():
    spec = OpenAPIBuilder().build(examples={})
    auth_operation = spec["paths"]["/settings/user-info"]["get"]

    assert spec["components"]["securitySchemes"]["BearerAuth"]["scheme"] == "bearer"
    assert auth_operation["security"] == [{"BearerAuth": []}]
    assert [item["name"] for item in auth_operation["parameters"][:3]] == [
        "Origin",
        "Referer",
        "User-Agent",
    ]


def test_build_uses_username_field_for_login_example():
    spec = OpenAPIBuilder().build(examples={})
    login_example = spec["paths"]["/auth/login"]["post"]["requestBody"]["content"][
        "application/json"
    ]["example"]

    assert "username" in login_example
    assert "login" not in login_example


def test_build_uses_array_schema_and_response_examples_for_list_endpoints():
    examples = {"/dashboard/chart/attendance": [{"date": "2026-04-18", "value": 1}]}
    spec = OpenAPIBuilder().build(examples=examples)
    response = spec["paths"]["/dashboard/chart/attendance"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]

    assert response["schema"]["type"] == "array"
    assert response["example"] == examples["/dashboard/chart/attendance"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_builder.py -v`
Expected: FAIL because `components`, `security`, required headers, and array schemas are not implemented yet.

- [ ] **Step 3: Commit**

```bash
git add tests/test_builder.py
git commit -m "test: add openapi enrichment coverage"
```

### Task 2: Update request example source and OpenAPI builder

**Files:**
- Modify: `src/collector/endpoints.py`
- Modify: `src/publisher/builder.py`
- Read: `src/validator/validator.py`

- [ ] **Step 1: Change the login request example source**

```python
params={
    "application_key": "",
    "id_city": None,
    "username": "<login>",
    "password": "<password>",
}
```

- [ ] **Step 2: Add module-level header docs and validator-backed schema selection**

```python
from src.collector.endpoints import ENDPOINTS, LOGIN_PATH
from src.validator.validator import MODELS as VALIDATOR_MODELS

REQUIRED_HEADERS = [
    {
        "name": "Origin",
        "in": "header",
        "required": True,
        "schema": {"type": "string"},
        "example": "https://journal.top-academy.ru",
        "description": "Required by the API CORS policy.",
    },
    ...
]
```

- [ ] **Step 3: Extend `build()` to emit auth scheme, per-operation security, requestBody description, required headers, and array/object response schemas**

```python
spec["components"] = {
    "securitySchemes": {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "JWT access token obtained from POST /auth/login response field `access_token`. "
                "Pass as: Authorization: Bearer <token>"
            ),
        }
    }
}

if endpoint.path in VALIDATOR_MODELS:
    _model, is_list = VALIDATOR_MODELS[endpoint.path]
    response_schema = {
        "type": "array",
        "items": {"type": "object", "additionalProperties": True},
    } if is_list else {"type": "object", "additionalProperties": True}
else:
    response_schema = {"type": "object", "additionalProperties": True}

if endpoint.path != LOGIN_PATH:
    operation["security"] = [{"BearerAuth": []}]
    existing_params = operation.get("parameters", [])
    operation["parameters"] = REQUIRED_HEADERS + existing_params
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_builder.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/collector/endpoints.py src/publisher/builder.py
git commit -m "feat: enrich openapi auth and response metadata"
```

### Task 3: Verify lint, tests, and generated spec

**Files:**
- Read: `documentation/openapi.json`
- Read: `main.py`

- [ ] **Step 1: Confirm anonymized examples are wired through the pipeline**

Run: `sed -n '40,90p' main.py`
Expected: `builder.build(examples=clean, is_api_down=is_api_down)` is present.

- [ ] **Step 2: Run lint and focused tests**

Run: `ruff check src/publisher/builder.py src/collector/endpoints.py`
Expected: All checks passed.

Run: `pytest tests/test_builder.py -v`
Expected: All builder tests pass.

- [ ] **Step 3: Rebuild and inspect generated OpenAPI**

Run: `python main.py`
Expected: `documentation/openapi.json` regenerated and `PIPELINE_OK` printed when credentials are available.

Run: `sed -n '1,260p' documentation/openapi.json`
Expected: `BearerAuth` exists, `/auth/login` shows `username`, authenticated endpoints include `Origin` and `Referer`, and list endpoints use array response schemas.

- [ ] **Step 4: Commit**

```bash
git add documentation/openapi.json
git commit -m "chore: verify openapi enrichment complete"
```

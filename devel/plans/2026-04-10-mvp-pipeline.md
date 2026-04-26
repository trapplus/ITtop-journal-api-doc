# MVP Journal API Pipeline Implementation Plan

**Goal:** Implement an end-to-end Python MVP pipeline that collects Journal API data, validates it, anonymizes sensitive fields, and publishes OpenAPI docs via GitHub Actions.

**Architecture:** CLI-style async collection + validation/anonymization/build steps, persisted to local artifacts under `data/` and `documentation/`. No web server, only scripts and static Swagger UI.

**Tech Stack:** Python 3.12, httpx (async), pydantic v2, faker, pytest, ruff, GitHub Actions.

---

## Task 1: Baseline project scaffolding and dependency files

**Files:**
- Modify: `.gitignore`
- Modify: `pyproject.toml`
- Create: `requirements.txt`
- Modify: `data/raw/.gitkeep`
- Modify: `data/examples/.gitkeep`
- Modify: `documentation/index.html`

Steps:
1. Fill dependency declarations and tool config.
2. Add runtime dependency mirror in `requirements.txt`.
3. Set ignore rules so real raw API responses are ignored.
4. Add static Swagger UI HTML page.

## Task 2: Write failing tests (RED)

**Files:**
- Modify: `tests/test_validator.py`
- Modify: `tests/test_anonymizer.py`
- Modify: `tests/test_builder.py`

Steps:
1. Add tests required by spec for validator/anonymizer/builder.
2. Run test subset and confirm failures due to missing implementation.

## Task 3: Implement collector and endpoint registry

**Files:**
- Modify: `src/collector/__init__.py`
- Modify: `src/collector/endpoints.py`
- Modify: `src/collector/client.py`

Steps:
1. Define `Endpoint` dataclass and `ENDPOINTS` list.
2. Implement `JournalClient` with auth, fetch, collect loop, and retries.

## Task 4: Implement validation layer

**Files:**
- Modify: `src/validator/__init__.py`
- Modify: `src/validator/models.py`
- Modify: `src/validator/validator.py`

Steps:
1. Add placeholder Pydantic models per endpoint (`extra='allow'`).
2. Add `MODELS` mapping.
3. Implement validation result collection and issue body rendering.

## Task 5: Implement anonymizer and publisher

**Files:**
- Modify: `src/anonymizer/__init__.py`
- Modify: `src/anonymizer/rules.py`
- Modify: `src/anonymizer/anonymizer.py`
- Modify: `src/publisher/__init__.py`
- Modify: `src/publisher/builder.py`

Steps:
1. Add faker replacement rules and recursive anonymization.
2. Build OpenAPI spec from endpoint registry and examples.
3. Add JSON save helper.

## Task 6: Wire pipeline entrypoint and CI workflow

**Files:**
- Create: `main.py`
- Modify: `.github/workflows/collect.yml`

Steps:
1. Implement orchestrated pipeline script.
2. Generate validation issue markdown artifact on failures.
3. Configure scheduled workflow, issue creation, and pages deployment.

## Task 7: GREEN + quality checks

**Files:**
- Potentially all touched files

Steps:
1. Run full test suite, fix failing behavior.
2. Run `ruff check .`, fix warnings.
3. Confirm final file layout and artifacts exist.

# Add Official Server to OpenAPI Spec

**Goal:** Добавить официальный сервер `msapi.top-academy.ru/api/v2` в список `servers` OpenAPI спека рядом с mock-сервером. Это позволяет делать запросы напрямую к реальному API из Swagger UI.

**Architecture:** Единственное изменение — `src/publisher/builder.py`, массив `servers` в методе `build()`. Тест на наличие mock-сервера уже есть, добавляем аналогичный для реального.

**Tech Stack:** Python 3.12, pytest

---

### Task 1: Добавить тест

**Files:**
- Modify: `tests/test_builder.py`

- [ ] **Step 1: Написать падающий тест**

```python
def test_build_contains_official_and_mock_servers():
    """Spec should list both the real API and the mock server."""

    spec = OpenAPIBuilder().build(examples={})
    urls = [s["url"] for s in spec["servers"]]

    assert "https://msapi.top-academy.ru/api/v2" in urls
    assert "https://ittop-mock.blazer19092008.workers.dev/api/v2" in urls
```

- [ ] **Step 2: Убедиться что тест падает**

```bash
pytest tests/test_builder.py::test_build_contains_official_and_mock_servers -v
# Expected: FAIL — official server отсутствует в spec["servers"]
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_builder.py
git commit -m "test: add assertion for official server in openapi servers list"
```

---

### Task 2: Добавить официальный сервер в builder

**Files:**
- Modify: `src/publisher/builder.py`

- [ ] **Step 1: Расширить список `servers` в методе `build()`**

Найти в `builder.py` блок:

```python
"servers": [
    {
        "url": "https://ittop-mock.blazer19092008.workers.dev/api/v2",
        "description": "Mock server (anonymized data, updated daily)",
    }
],
```

Заменить на:

```python
"servers": [
    {
        "url": "https://msapi.top-academy.ru/api/v2",
        "description": "Official API server (requires valid Bearer token)",
    },
    {
        "url": "https://ittop-mock.blazer19092008.workers.dev/api/v2",
        "description": "Mock server (anonymized data, updated daily)",
    },
],
```

- [ ] **Step 2: Убедиться что тест проходит**

```bash
pytest tests/test_builder.py -v
# Expected: все тесты PASS
```

- [ ] **Step 3: Commit**

```bash
git add src/publisher/builder.py
git commit -m "feat: add official api server to openapi servers list"
```

---

### Task 3: Пересобрать openapi.json

**Files:**
- Modify: `documentation/openapi.json`

- [ ] **Step 1: Пересобрать спек**

```bash
JOURNAL_LOGIN=... JOURNAL_PASSWORD=... uv run main.py
# или без credentials если хочешь только спек без сбора:
python -c "
from src.publisher.builder import OpenAPIBuilder
b = OpenAPIBuilder()
b.save(b.build(examples={}))
print('done')
"
```

- [ ] **Step 2: Проверить что оба сервера в файле**

```bash
jq '.servers[].url' documentation/openapi.json
# Expected:
# "https://msapi.top-academy.ru/api/v2"
# "https://ittop-mock.blazer19092008.workers.dev/api/v2"
```

- [ ] **Step 3: Commit**

```bash
git add documentation/openapi.json
git commit -m "chore: rebuild openapi with official server added"
```
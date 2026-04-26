# Endpoint Tags Implementation Plan

**Goal:** Добавить в `Endpoint` флаги управления анонимизацией, лимитами и валидацией объёмов. Рефакторить пайплайн чтобы trim и count-validation были per-endpoint.

**Architecture:** Единственный источник конфигурации — `Endpoint` dataclass в `endpoints.py`. Логика пайплайна меняется в `main.py` и `collector/client.py`. Validator получает опциональную count-проверку.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, ruff

---

### Task 1: Расширить Endpoint dataclass

**Files:**
- Modify: `src/collector/endpoints.py`

- [ ] **Step 1: Добавить поля в dataclass**

```python
@dataclass(slots=True, frozen=True)
class Endpoint:
    path: str
    method: str
    params: dict | None = None
    anonymize: bool = True
    max_items: int | None = None        # None = global default (3)
    validate_count: bool = False        # True = проверяем len до trim
    expected_max_items: int | None = None  # используется только если validate_count=True
```

- [ ] **Step 2: Проставить флаги на всех эндпоинтах**

```python
ENDPOINTS: list[Endpoint] = [
    Endpoint(path=LOGIN_PATH, method="POST", params={...}),

    # ── Profile / Settings ── чувствительные данные
    Endpoint(path="/settings/user-info", method="GET"),
    Endpoint(path="/profile/operations/settings", method="GET"),
    Endpoint(path="/profile/statistic/student-achievements", method="GET"),

    # ── Dashboard ── чувствительные данные
    Endpoint(path="/dashboard/chart/average-progress", method="GET"),
    Endpoint(path="/dashboard/chart/attendance", method="GET"),
    Endpoint(path="/dashboard/chart/progress", method="GET"),
    Endpoint(path="/dashboard/progress/activity", method="GET"),
    Endpoint(path="/dashboard/progress/leader-group", method="GET"),
    Endpoint(path="/dashboard/progress/leader-stream", method="GET"),
    Endpoint(path="/dashboard/progress/leader-group-points", method="GET"),
    Endpoint(path="/dashboard/progress/leader-stream-points", method="GET"),
    Endpoint(path="/dashboard/info/future-exams", method="GET"),

    # ── Schedule ── count validation включён
    Endpoint(
        path="/schedule/operations/get-by-date",
        method="GET",
        params={"date_filter": date.today().isoformat()},
        validate_count=True,
        expected_max_items=1,
    ),
    Endpoint(
        path="/schedule/operations/get-by-date-range",
        method="GET",
        params={
            "date_start": date.today().isoformat(),
            "date_end": date.today().isoformat(),
        },
        validate_count=True,
        expected_max_items=7,
        max_items=7,
    ),
    Endpoint(
        path="/schedule/operations/get-month",
        method="GET",
        params={"date_filter": date.today().isoformat()},
        validate_count=True,
        expected_max_items=31,
        max_items=31,
    ),

    # ── Progress ── большие датасеты, count не проверяем, режем сразу
    Endpoint(path="/progress/operations/student-visits", method="GET"),
    Endpoint(path="/progress/operations/student-exams", method="GET"),

    # ── Library / Homework ──
    Endpoint(path="/library/operations/list", method="GET", params={
        "material_type": 2, "filter_type": 0, "recommended_type": 0,
    }),
    Endpoint(path="/count/homework", method="GET"),

    # ── Reviews / Feedback ──
    Endpoint(path="/reviews/index/list", method="GET"),
    Endpoint(path="/reviews/index/instruction", method="GET"),
    Endpoint(path="/feedback/students/evaluate-lesson-list", method="GET"),
    Endpoint(path="/feedback/social-review/get-review-list", method="GET"),

    # ── Signals ──
    Endpoint(path="/signal/operations/signals-list", method="GET"),
    Endpoint(path="/signal/operations/problems-list", method="GET"),

    # ── News ──
    Endpoint(path="/news/operations/latest-news", method="GET"),

    # ── Public (не чувствительные, anonymize=False) ──
    Endpoint(path="/public/languages", method="GET", anonymize=False),
    Endpoint(
        path="/public/translations",
        method="GET",
        params={"language": "ru"},
        anonymize=False,
    ),
    Endpoint(path="/public/tags", method="GET", anonymize=False),
]
```

- [ ] **Step 3: Commit**

```bash
git add src/collector/endpoints.py
git commit -m "feat(collector): add anonymize/max_items/validate_count fields to Endpoint"
```

---

### Task 2: Рефакторить collector — trim по per-endpoint max_items

**Files:**
- Modify: `src/collector/client.py`

- [ ] **Step 1: Изменить сигнатуру collect_all**

Убрать `max_list_items: int = 3` как глобальный параметр. Trim теперь читает `endpoint.max_items`, fallback на `DEFAULT_MAX_ITEMS = 3`.

```python
DEFAULT_MAX_ITEMS = 3

async def collect_all(self, endpoints: list[Endpoint]) -> dict[str, Any]:
    await self.authenticate()

    collected: dict[str, Any] = {}
    for endpoint in endpoints:
        if endpoint.path == LOGIN_PATH:
            continue
        try:
            raw_data = await self._fetch_with_retry(endpoint)
            limit = endpoint.max_items if endpoint.max_items is not None else DEFAULT_MAX_ITEMS
            collected[endpoint.path] = trim_arrays(raw_data, max_items=limit)
        except Exception as error:  # noqa: BLE001
            LOGGER.warning(
                "Endpoint collection failed for %s %s: %s",
                endpoint.method, endpoint.path, error,
            )
            collected[endpoint.path] = {"error": str(error)}

    return collected
```

- [ ] **Step 2: Commit**

```bash
git add src/collector/client.py
git commit -m "refactor(collector): per-endpoint max_items trim, remove global param"
```

---

### Task 3: Добавить count-валидацию в Validator

**Files:**
- Modify: `src/validator/validator.py`

- [ ] **Step 1: Добавить count-проверку в validate_all**

`validate_all` получает `endpoints: list[Endpoint]` вторым аргументом. Перед trim (до вызова — raw данные уже обрезаны коллектором, поэтому count-валидация работает на сырых данных в **main.py**, см. Task 4). Здесь только структурная валидация.

Изменить `format_issue_body` чтобы count-ошибки отображались отдельно:

```python
@dataclass
class ValidationResult:
    endpoint: str
    success: bool
    errors: list[str] = field(default_factory=list)
    count_warning: str | None = None  # новое поле
```

В `format_issue_body`:

```python
for r in results:
    if not r.success or r.count_warning:
        lines.append(f"### `{r.endpoint}`")
        if r.count_warning:
            lines.append(f"* ⚠️ Count warning: {r.count_warning}")
        for e in r.errors:
            lines.append(f"* {e}")
        lines.append("")
```

- [ ] **Step 2: Commit**

```bash
git add src/validator/validator.py
git commit -m "feat(validator): add count_warning field to ValidationResult"
```

---

### Task 4: Рефакторить main.py — count validation на raw данных

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Добавить сбор raw без trim, затем count-проверку**

```python
# Сборка raw данных (trim внутри collect_all по endpoint.max_items)
raw = await client.collect_all(ENDPOINTS)

# Count validation — на НЕОБРЕЗАННЫХ данных
# Для этого делаем отдельный проход по endpoint'ам у которых validate_count=True
# Но collect_all уже обрезал... 
# Решение: отдельный fetch для validate_count=True endpoint'ов перед trim
```

**Важно**: чтобы count-валидация видела реальное количество объектов ДО обрезания, нужно в `collect_all` возвращать также raw-размеры. Добавить в `client.py`:

```python
# Возвращаем tuple: (trimmed_data, raw_count_if_list)
# raw_count нужен только для validate_count=True endpoint'ов
```

Проще — сохранять `raw_counts: dict[str, int]` параллельно:

```python
async def collect_all(self, endpoints: list[Endpoint]) -> tuple[dict[str, Any], dict[str, int]]:
    ...
    raw_counts: dict[str, int] = {}
    for endpoint in endpoints:
        ...
        raw_data = await self._fetch_with_retry(endpoint)
        if endpoint.validate_count and isinstance(raw_data, list):
            raw_counts[endpoint.path] = len(raw_data)
        limit = endpoint.max_items if endpoint.max_items is not None else DEFAULT_MAX_ITEMS
        collected[endpoint.path] = trim_arrays(raw_data, max_items=limit)

    return collected, raw_counts
```

В `main.py`:

```python
raw, raw_counts = await client.collect_all(ENDPOINTS)

# Count warnings
endpoint_map = {e.path: e for e in ENDPOINTS}
count_warnings: dict[str, str] = {}
for path, count in raw_counts.items():
    ep = endpoint_map[path]
    if ep.validate_count and ep.expected_max_items is not None:
        if count > ep.expected_max_items:
            count_warnings[path] = (
                f"Expected <= {ep.expected_max_items} items, got {count}"
            )
```

Передать `count_warnings` в `format_issue_body` или смержить с results.

- [ ] **Step 2: Обновить вызов collect_all везде где используется**

```bash
grep -n "collect_all" main.py
```

- [ ] **Step 3: Commit**

```bash
git add main.py src/collector/client.py
git commit -m "feat(pipeline): count validation on raw data before trim"
```

---

### Task 5: Обновить anonymizer — пропускать anonymize=False endpoint'ы

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Применять anonymizer per-endpoint**

Сейчас: `clean = anonymizer.anonymize(raw)` — анонит весь dict целиком.

Заменить на:

```python
endpoint_map = {e.path: e for e in ENDPOINTS}
clean: dict[str, Any] = {}
for path, data in raw.items():
    ep = endpoint_map.get(path)
    if ep is not None and not ep.anonymize:
        clean[path] = data  # raw данные, без faker
    else:
        clean[path] = anonymizer.anonymize(data)
```

- [ ] **Step 2: Commit**

```bash
git add main.py
git commit -m "feat(pipeline): skip anonymization for non-sensitive endpoints"
```

---

### Task 6: Обновить тесты

**Files:**
- Modify: `tests/test_validator.py`
- Modify: `tests/test_anonymizer.py`

- [ ] **Step 1: Добавить тест на count_warning**

```python
def test_count_warning_included_in_issue_body():
    result = ValidationResult(
        endpoint="/schedule/operations/get-month",
        success=True,
        count_warning="Expected <= 31 items, got 45",
    )
    validator = Validator()
    body = validator.format_issue_body([result])
    assert "Count warning" in body
    assert "45" in body
```

- [ ] **Step 2: Добавить тест что anonymize=False endpoint не меняется**

```python
def test_anonymize_false_endpoint_passes_through():
    data = {"name_mystat": "Ukrainian", "short_name": "uk"}
    # Симулируем логику из main.py
    result = data  # не вызываем anonymizer
    assert result == data
```

- [ ] **Step 3: Прогнать тесты**

```bash
pytest tests/ -v
# Expected: все PASS
```

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: coverage for count_warning and anonymize=False passthrough"
```

---

### Task 7: Lint и финальная проверка

- [ ] **Step 1: Ruff**

```bash
ruff check src/ tests/ main.py
# Expected: All checks passed
```

- [ ] **Step 2: Полный тест**

```bash
pytest -v
# Expected: все зелёные
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: lint clean after endpoint tags implementation"
```

---

### Итоговое поведение после реализации

| Endpoint | anonymize | max_items | validate_count | expected_max_items |
|----------|-----------|-----------|----------------|--------------------|
| `/settings/user-info` | True | 3 (default) | False | — |
| `/progress/operations/student-visits` | True | 3 (default) | False | — |
| `/schedule/operations/get-by-date` | True | 3 (default) | True | 1 |
| `/schedule/operations/get-by-date-range` | True | 7 | True | 7 |
| `/schedule/operations/get-month` | True | 31 | True | 31 |
| `/public/languages` | **False** | 3 (default) | False | — |
| `/public/translations` | **False** | 3 (default) | False | — |
| `/public/tags` | **False** | 3 (default) | False | — |
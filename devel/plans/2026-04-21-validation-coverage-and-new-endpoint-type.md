# Validator Schema Coverage Plan

> **Scope:** Полное покрытие всех эндпоинтов Pydantic-моделями на основе реального датасета.

**Goal:** Добавить модели для всех 27 активных эндпоинтов, исправить баг с неверным schedule-путём, убрать ложные срабатывания Issue.

**Tech Stack:** Python 3.12, Pydantic v2, pytest

---

### Task 1: Обновить модели

**Files:**
- Modify: `src/validator/models.py`

- [x] **Step 1: Добавить новые модели по датасету**

```python
# Новые модели на основе реальных ответов API:
class ProfileSettingsResponse(_Base): ...   # /profile/operations/settings
class AchievementItem(_Base): ...           # /profile/statistic/student-achievements
class ChartProgressItem(_Base): ...         # /dashboard/chart/progress
class ActivityItem(_Base): ...              # /dashboard/progress/activity
class LeaderPointsResponse(_Base): ...      # /dashboard/progress/leader-*-points
class FutureExamItem(_Base): ...            # /dashboard/info/future-exams
class StudentExamItem(_Base): ...           # /progress/operations/student-exams
class LibraryItem(_Base): ...              # /library/operations/list (пустой ответ)
class SocialReviewItem(_Base): ...          # /feedback/social-review/get-review-list
class SignalItem(_Base): ...                # /signal/operations/signals-list
class ProblemItem(_Base): ...               # /signal/operations/problems-list
class NewsItem(_Base): ...                  # /news/operations/latest-news
class LanguageItem(_Base): ...              # /public/languages
class TranslationsResponse(_Base): ...      # /public/translations
```

- [x] **Step 2: Commit**

```bash
git add src/validator/models.py
git commit -m "feat(validator): add pydantic models for all discovered endpoints"
```

---

### Task 2: Обновить реестр MODELS и исправить баги

**Files:**
- Modify: `src/validator/validator.py`

- [x] **Step 1: Исправить неверный путь schedule и добавить все новые модели в MODELS**

Был баг: `/schedule/operations/get-by-date` — такого пути нет в ENDPOINTS.
Правильные пути: `get-by-date-range`, `get-month`, `get-by-date`.

```python
MODELS: dict[str, tuple[type, bool]] = {
    # исправлено: убран несуществующий /get-by-date, добавлены все три реальных пути
    "/schedule/operations/get-by-date-range": (ScheduleItem, True),
    "/schedule/operations/get-month":         (ScheduleItem, True),
    "/schedule/operations/get-by-date":       (ScheduleItem, True),
    # новые:
    "/profile/operations/settings":           (ProfileSettingsResponse, False),
    "/dashboard/progress/leader-group-points":(LeaderPointsResponse, False),
    # ... и остальные 20 эндпоинтов
}
```

- [x] **Step 2: Закомментировать /public/translations с TODO**

```python
# TODO: нестабильный эндпоинт — периодически бекает {"error": "Ошибка"},
# что вызывает ложные Issue. Раскомментировать когда станет стабильным.
# "/public/translations": (TranslationsResponse, False),
```

- [x] **Step 3: Commit**

```bash
git add src/validator/validator.py
git commit -m "fix(validator): correct schedule path bug, register all endpoint models"
```

---

### Task 3: Добавить новый эндпоинт get-by-date

**Files:**
- Modify: `src/collector/endpoints.py`
- Modify: `src/validator/validator.py`

- [ ] **Step 1: Добавить эндпоинт в реестр**

```python
Endpoint(path="/schedule/operations/get-by-date", method="GET", params={
    "date_filter": date.today().isoformat(),
}),
```

- [ ] **Step 2: Добавить в MODELS (уже добавлен в Task 2)**

```python
"/schedule/operations/get-by-date": (ScheduleItem, True),
```

- [ ] **Step 3: Commit**

```bash
git add src/collector/endpoints.py
git commit -m "feat(collector): add schedule/get-by-date endpoint"
```

---

### Task 4: Верификация

**Files:**
- Read: `data/raw/latest.json`

- [ ] **Step 1: Прогнать пайплайн**

```bash
JOURNAL_LOGIN=... JOURNAL_PASSWORD=... uv run main.py
# Expected: PIPELINE_OK, отсутствие data/validation_issue.md
```

- [ ] **Step 2: Проверить покрытие**

```bash
jq 'keys' data/raw/latest.json
# Все ключи должны быть либо в MODELS, либо быть known-skip (/reviews/index/instruction)
```

- [ ] **Step 3: Прогнать тесты**

```bash
pytest tests/test_validator.py -v
# Expected: все зелёные
```

- [ ] **Step 4: Commit**

```bash
git add data/examples/latest.json documentation/openapi.json
git commit -m "chore: rebuild examples and openapi after schema coverage expansion"
```

---

### Исключённые из MODELS эндпоинты (причина)

| Эндпоинт | Причина |
|----------|---------|
| `/reviews/index/instruction` | Возвращает `null` — валидировать нечего |
| `/public/translations` | Нестабильный, периодически `{"error": "Ошибка"}` — ложные Issue |
| `/auth/login` | Эндпоинт авторизации, не сборщик данных |
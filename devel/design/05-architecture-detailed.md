# Архитектура — Детальная

---

## Структура проекта

```
project/
├── .github/
│   └── workflows/
│       └── collect.yml          # Запуск pipeline раз в 24ч
├── src/
│   ├── collector/
│   │   ├── __init__.py
│   │   ├── client.py            # httpx: авторизация, запросы к эндпоинтам, retry
│   │   └── endpoints.py         # Список известных эндпоинтов и методов
│   ├── validator/
│   │   ├── __init__.py
│   │   ├── models.py            # Pydantic модели для каждого эндпоинта
│   │   └── validator.py         # Запуск валидации, сбор ошибок
│   ├── anonymizer/
│   │   ├── __init__.py
│   │   └── anonymizer.py        # Faker-замены по правилам из rules.py
│   │   └── rules.py             # Маппинг полей → тип замены (имя, id, дата...)
│   └── publisher/
│       ├── __init__.py
│       ├── builder.py           # Сборка openapi.json из моделей + примеров
│       └── templates/
│           └── swagger/         # Статика Swagger UI (index.html, swagger-ui.js...)
├── data/
│   ├── raw/                     # Сырые JSON от collector (в .gitignore)
│   └── examples/                # Анонимизированные примеры (коммитятся)
├── documentation/
│   └── openapi.json             # Финальный артефакт → GitHub Pages
├── tests/
│   ├── test_validator.py
│   ├── test_anonymizer.py
│   └── test_builder.py
├── pyproject.toml
└── .gitignore                   # data/raw/ обязательно здесь
```

---

## Компонент: Collector

### Ответственность
Авторизоваться в Journal, обойти все известные эндпоинты, сохранить сырые ответы как JSON.

### Внутренняя структура

| Модуль | Роль |
|--------|------|
| `client.py` | HTTP-клиент: логин, сессия, GET/POST запросы, retry |
| `endpoints.py` | Список `Endpoint(path, method, params)` |

### Ключевые интерфейсы

```python
# endpoints.py
@dataclass
class Endpoint:
    path: str
    method: str  # GET | POST
    params: dict | None = None

ENDPOINTS: list[Endpoint] = [...]

# client.py
class JournalClient:
    def __init__(self, login: str, password: str): ...
    def collect_all(self, endpoints: list[Endpoint]) -> dict[str, Any]:
        """Возвращает {endpoint_path: raw_response_json}"""
```

### Зависимости
- `httpx` — async HTTP-запросы к Journal API
- `os.environ` — `JOURNAL_LOGIN`, `JOURNAL_PASSWORD` из GitHub Secrets

---

## Компонент: Validator

### Ответственность
Проверить сырые данные на соответствие Pydantic моделям, собрать diff если что-то изменилось.

### Внутренняя структура

| Модуль | Роль |
|--------|------|
| `models.py` | Pydantic модели по одной на каждый эндпоинт |
| `validator.py` | Прогон данных через модели, сбор `ValidationError` |

### Ключевые интерфейсы

```python
# validator.py
@dataclass
class ValidationResult:
    endpoint: str
    success: bool
    errors: list[str]  # список полей с описанием что сломалось

class Validator:
    def validate_all(self, raw: dict[str, Any]) -> list[ValidationResult]:
        """Возвращает результат по каждому эндпоинту"""
    
    def has_failures(self, results: list[ValidationResult]) -> bool: ...
```

### Зависимости
- `pydantic` v2

---

## Компонент: Anonymizer

### Ответственность
Заменить реальные значения в JSON на синтетические по правилам маппинга.

### Внутренняя структура

| Модуль | Роль |
|--------|------|
| `rules.py` | `RULES: dict[str, Callable]` — имя поля → faker-функция |
| `anonymizer.py` | Рекурсивный обход JSON, применение правил |

### Ключевые интерфейсы

```python
# rules.py
from faker import Faker
fake = Faker()

RULES: dict[str, Callable] = {
    "fio":        lambda: fake.name(),
    "id":         lambda: fake.random_int(10000, 99999),
    "email":      lambda: fake.email(),
    "phone":      lambda: fake.phone_number(),
    "created_at": lambda: fake.iso8601(),
    # ...добавляй по мере обнаружения полей
}

# anonymizer.py
class Anonymizer:
    def anonymize(self, data: dict | list) -> dict | list:
        """Рекурсивно заменяет значения согласно RULES"""
```

### Зависимости
- `faker`

---

## Компонент: Publisher

### Ответственность
Собрать `openapi.json` из Pydantic моделей и анонимизированных примеров, подготовить GitHub Pages.

### Внутренняя структура

| Модуль | Роль |
|--------|------|
| `builder.py` | Генерация openapi.json: info + paths + examples |
| `templates/swagger/` | Статика Swagger UI (скачивается один раз, коммитится) |

### Ключевые интерфейсы

```python
# builder.py
class OpenAPIBuilder:
    def build(
        self,
        endpoints: list[Endpoint],
        models: dict[str, type[BaseModel]],
        examples: dict[str, Any],
        is_api_down: bool = False,
    ) -> dict:
        """Возвращает готовый openapi dict"""
    
    def save(self, spec: dict, path: str = "documentation/openapi.json") -> None: ...
```

### Зависимости
- `pydantic` (`.model_json_schema()`)
- стандартный `json`

---

## GitHub Actions Pipeline

```yaml
# .github/workflows/collect.yml
on:
  schedule:
    - cron: '0 3 * * *'   # раз в сутки в 03:00 UTC
  workflow_dispatch:        # ручной запуск

jobs:
  collect:
    steps:
      - collect      → src/collector (auth: username+password+application_key)
      - validate     → src/validator (model, is_list dispatch)
                       on failure: writes data/validation_issue.md
                       sets GITHUB_OUTPUT validation_failed=true
      - anonymize    → src/anonymizer (recursive type-based faker)
      - build        → src/publisher (openapi.json → documentation/)
      - deploy       → peaceiris/actions-gh-pages → GitHub Pages
      - issue        → peter-evans/create-issue-from-file
                       only if validation_failed == 'true'
```

---

## Обработка ошибок

| Ситуация | Поведение |
|----------|-----------|
| Валидация не прошла | GitHub Action падает, бот открывает Issue с логом полей |
| API не отвечает | Retry x3 с паузой 10 мин, затем прокси, затем пауза 24ч |
| Rate limit | Retry через 5 мин, при повторе — Issue |
| Ошибка авторизации | Немедленная остановка, Issue |
| CI issue spam | `hashFiles()` читает repo, а не runtime-файл → использовать step output |

---

## Логирование

- Формат: структурированный текст (stdout)
- В GitHub Actions: виден в логах джобы
- Уровни: `INFO` (шаги), `WARNING` (retry), `ERROR` (fail + тело для Issue)

---

## Чеклист

- [x] Каждый компонент имеет одну чёткую ответственность
- [x] Зависимости между компонентами однонаправленные
- [x] Нет циклических зависимостей
- [x] Ошибки обрабатываются на каждом уровне
- [x] Реальные данные не покидают `data/raw/` (в .gitignore)

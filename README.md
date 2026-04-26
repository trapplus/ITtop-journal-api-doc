# ITtop Journal API Docs

> Автоматическая OpenAPI документация для [IT Top Academy Journal](https://journal.top-academy.ru).  
> Данные собираются раз в сутки, анонимизируются и публикуются через GitHub Pages.

## Что это

IT Top Journal не имеет публичной документации. Этот проект:

- Собирает реальные ответы API через авторизованные запросы
- Валидирует их через Pydantic — если структура изменилась, открывается GitHub Issue
- Анонимизирует данные через Faker — реальные имена, ID и даты не публикуются
- Генерирует `openapi.json` и публикует Swagger UI на GitHub Pages

**Документация обновляется автоматически каждые 24 часа.**

## For AI Agents

All AI agents working in this repo follow the shared rules in [`AGENTS.md`](AGENTS.md). Read it first.
Agent-specific files add only what's unique to each tool — no duplication:

| File | Tool | Purpose |
|------|------|---------|
| [`AGENTS.md`](AGENTS.md) | All | Shared rules — single source of truth |
| [`CLAUDE.md`](CLAUDE.md) | Claude Code | TDD enforcement, verification mandate |
| [`GEMINI.md`](GEMINI.md) | Gemini CLI | Lifecycle phases, decision protocol |
| [`.codex/AGENTS.md`](.codex/AGENTS.md) | Codex | Style rules, superpowers setup |

## Структура

```
src/
  collector/     Авторизация и сбор данных с эндпоинтов
  validator/     Pydantic-модели и валидация ответов
  anonymizer/    Faker-замена реальных значений
  publisher/     Генерация openapi.json и Swagger UI
data/
  raw/           Сырые ответы API (в .gitignore)
  examples/      Анонимизированные примеры (коммитятся)
documentation/   Артефакт для GitHub Pages
devel/
  design/        Архитектурные решения
  plans/         Планы реализации
  changelog/     История изменений
tests/           Pytest-тесты
```

## Setup

```bash
uv sync &uv lock
uv run main.py
```

## Запуск

```bash
JOURNAL_LOGIN=your_login JOURNAL_PASSWORD=your_password python main.py
```

Результат:
- `data/raw/latest.json` — сырые ответы (не коммитится)
- `data/examples/latest.json` — анонимизированные примеры
- `documentation/openapi.json` — готовый OpenAPI спек

## Тесты

```bash
pytest
ruff check .
```

## Покрытые эндпоинты

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/auth/login` | POST | Авторизация, получение Bearer токена |
| `/settings/user-info` | GET | Профиль студента, группа, поток |
| `/dashboard/chart/average-progress` | GET | График среднего прогресса по месяцам |
| `/dashboard/chart/attendance` | GET | График посещаемости по месяцам |
| `/dashboard/progress/leader-group` | GET | Топ студентов по группе |
| `/dashboard/progress/leader-stream` | GET | Топ студентов по потоку |
| `/progress/operations/student-visits` | GET | Журнал посещений и оценок |
| `/count/homework` | GET | Счётчики домашних заданий по типам |
| `/schedule/operations/get-by-date` | GET | Расписание на дату (`?date=YYYY-MM-DD`) |
| `/reviews/index/list` | GET | Отзывы преподавателей |
| `/feedback/students/evaluate-lesson-list` | GET | Список уроков для оценки |
| `/public/tags` | GET | Публичные теги |

## Аутентификация

Все эндпоинты кроме `/auth/login` требуют:

```
Authorization: Bearer <access_token>
Origin: https://journal.top-academy.ru
Referer: https://journal.top-academy.ru/
```

Токен получается через POST `/auth/login`:

```json
{
  "application_key": "<key>",
  "id_city": null,
  "username": "<login>",
  "password": "<password>"
}
```

## Мониторинг изменений API

Если структура ответа изменилась — пайплайн падает и открывает GitHub Issue с описанием конкретных полей которые перестали проходить валидацию.

## Планы

### Ближайшее

- [X] Добавить `BearerAuth` security scheme в OpenAPI спек
- [X] Задокументировать обязательные headers (`Origin`, `Referer`) как parameters
- [X] Исправить схему ответов (`array` vs `object`) на основе реальных данных

### Позже

- [ ] Текстовая документация по каждому эндпоинту на основе реальных примеров — типы полей, возможные значения, семантика
- [ ] Документирование enum-значений (`status_was`, `counter_type`, `gender`, `group_status`)
- [X] Покрытие дополнительных эндпоинтов по мере обнаружения (В процессе, большая часть основных endpoint задокументирована)
- [ ] Changelog автоматически генерируемый из issue истории изменений API
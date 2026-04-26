# Cloudflare Worker CORS Proxy Plan

**Goal:** Превратить Worker в CORS-прокси: с Bearer токеном — проксирует на реальный API, без токена — отдаёт mock-данные. Один сервер в Swagger UI, CORS решён.

**Architecture:** Worker проверяет наличие `Authorization` заголовка. Есть — форвардит запрос на `msapi.top-academy.ru/api/v2` с нужными хедерами и возвращает реальный ответ. Нет — отдаёт из `MOCK` объекта как сейчас. `build_worker.py` обновляется чтобы генерировать новую логику.

**Tech Stack:** Cloudflare Workers, Python 3.12, pytest

---

### Task 1: Обновить `build_worker.py`

**Files:**
- Modify: `scripts/build_worker.py`

- [ ] **Step 1: Заменить шаблон Worker-а**

Найти функцию `_render_worker` и заменить возвращаемый шаблон:

```python
REAL_API_BASE = "https://msapi.top-academy.ru/api/v2"
API_PREFIX = "/api/v2"

def _render_worker(mock_payloads: dict[str, object]) -> str:
    mock_json = json.dumps(mock_payloads, ensure_ascii=False, indent=2)
    return f"""const MOCK = {mock_json};

const REAL_API_BASE = "{REAL_API_BASE}";

const CORS_HEADERS = {{
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
  "Access-Control-Allow-Headers": "*",
  "Content-Type": "application/json; charset=utf-8",
}};

function normalizePath(pathname) {{
  if (pathname === "{API_PREFIX}") return "/";
  if (pathname.startsWith("{API_PREFIX}/")) return pathname.slice({len(API_PREFIX)});
  return pathname;
}}

function jsonResponse(body, status = 200) {{
  return new Response(JSON.stringify(body), {{
    status,
    headers: CORS_HEADERS,
  }});
}}

// Проксируем запрос на реальный API, добавляя обязательные хедеры.
// Authorization пробрасывается из оригинального запроса (Bearer токен юзера).
async function proxyToRealApi(request, apiPath) {{
  const targetUrl = REAL_API_BASE + apiPath + new URL(request.url).search;

  const proxyRequest = new Request(targetUrl, {{
    method: request.method,
    headers: {{
      "Authorization": request.headers.get("Authorization") ?? "",
      "Origin": "https://journal.top-academy.ru",
      "Referer": "https://journal.top-academy.ru/",
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
      "Content-Type": "application/json",
    }},
    body: request.method !== "GET" ? request.body : undefined,
  }});

  const realResponse = await fetch(proxyRequest);
  const body = await realResponse.text();

  // Прокидываем реальный статус-код, но добавляем наши CORS-хедеры
  return new Response(body, {{
    status: realResponse.status,
    headers: CORS_HEADERS,
  }});
}}

export default {{
  async fetch(request) {{
    // Preflight CORS запрос от браузера — отвечаем сразу
    if (request.method === "OPTIONS") {{
      return new Response(null, {{ status: 204, headers: CORS_HEADERS }});
    }}

    const apiPath = normalizePath(new URL(request.url).pathname);
    const hasToken = request.headers.has("Authorization");

    // Если есть Bearer токен — проксируем на реальный API
    if (hasToken) {{
      return proxyToRealApi(request, apiPath);
    }}

    // Без токена — отдаём mock
    const payload = MOCK[apiPath];
    if (payload === undefined) {{
      return jsonResponse({{ error: "Not found", path: apiPath }}, 404);
    }}

    return jsonResponse(payload);
  }},
}};
"""
```

- [ ] **Step 2: Добавить константу `REAL_API_BASE` на уровень модуля**

В начале файла рядом с `EXAMPLES_PATH`:

```python
REAL_API_BASE = "https://msapi.top-academy.ru/api/v2"
API_PREFIX = "/api/v2"
```

- [ ] **Step 3: Commit**

```bash
git add scripts/build_worker.py
git commit -m "feat(worker): add cors proxy mode when bearer token present"
```

---

### Task 2: Обновить `builder.py` — один сервер вместо двух

**Files:**
- Modify: `src/publisher/builder.py`

Теперь Worker — единственный сервер. Официальный `msapi.top-academy.ru` убираем —
он недоступен из браузера из-за CORS, смысла нет.

- [ ] **Step 1: Обновить константу `SERVERS`**

```python
# Worker выступает единственной точкой входа:
# — с Bearer токеном → проксирует на реальный API (живые данные)
# — без токена       → отдаёт mock (анонимизированные данные)
# Прямой доступ к msapi.top-academy.ru из браузера невозможен из-за CORS.
SERVERS = [
    {
        "url": "https://ittop-mock.blazer19092008.workers.dev/api/v2",
        "description": "Mock + proxy server: без токена — mock-данные, с Bearer токеном — реальный API",
    },
]
```

- [ ] **Step 2: Commit**

```bash
git add src/publisher/builder.py
git commit -m "fix(builder): single worker server, remove unreachable official url"
```

---

### Task 3: Обновить тест под новую логику серверов

**Files:**
- Modify: `tests/test_builder.py`

- [ ] **Step 1: Заменить тест серверов**

Удалить `test_build_contains_official_and_mock_servers`, добавить:

```python
def test_build_contains_single_worker_server():
    """Spec should list only the Worker as server.

    Worker сам решает куда идти: mock или реальный API.
    Прямой msapi.top-academy.ru недоступен из браузера (CORS).
    """

    spec = OpenAPIBuilder().build(examples={})

    assert len(spec["servers"]) == 1
    assert spec["servers"][0]["url"] == "https://ittop-mock.blazer19092008.workers.dev/api/v2"
```

- [ ] **Step 2: Прогнать тесты**

```bash
pytest tests/test_builder.py -v
# Expected: все PASS
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_builder.py
git commit -m "test(builder): update server assertion for single worker endpoint"
```

---

### Task 4: Пересобрать Worker и задеплоить

**Files:**
- Modify: `data/examples/latest.json` (уже есть)
- Modify: `mock/worker.js` (генерируется)

- [ ] **Step 1: Пересобрать Worker**

```bash
python scripts/build_worker.py
```

- [ ] **Step 2: Проверить что прокси-логика попала в файл**

```bash
grep "proxyToRealApi" mock/worker.js
# Expected: строка найдена
```

- [ ] **Step 3: Задеплоить**

```bash
cd mock && npx wrangler deploy
```

- [ ] **Step 4: Проверить mock (без токена)**

```bash
curl https://ittop-mock.blazer19092008.workers.dev/api/v2/reviews/index/list
# Expected: анонимизированные данные из MOCK
```

- [ ] **Step 5: Проверить прокси (с токеном)**

```bash
curl -H "Authorization: Bearer <твой_токен>" \
     -H "accept: application/json" \
     https://ittop-mock.blazer19092008.workers.dev/api/v2/reviews/index/list
# Expected: реальные данные с msapi.top-academy.ru
```

- [ ] **Step 6: Пересобрать openapi.json**

```bash
python -c "
from src.publisher.builder import OpenAPIBuilder
b = OpenAPIBuilder()
b.save(b.build(examples={}))
print('done')
"
```

- [ ] **Step 7: Commit**

```bash
git add documentation/openapi.json
git commit -m "chore: rebuild openapi after worker proxy update"
```

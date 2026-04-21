"""Build a Cloudflare Worker mock server from anonymized example payloads.

Worker работает в двух режимах:
- Без Authorization header → отдаёт mock-данные из MOCK объекта
- С Authorization header  → проксирует запрос на реальный API, добавляя
                            обязательные CORS-хедеры к ответу
"""

from __future__ import annotations

import json
from pathlib import Path

EXAMPLES_PATH = Path("data/examples/latest.json")
WORKER_PATH = Path("mock/worker.js")

REAL_API_BASE = "https://msapi.top-academy.ru/api/v2"
API_PREFIX = "/api/v2"


def _render_worker(mock_payloads: dict[str, object]) -> str:
    mock_json = json.dumps(mock_payloads, ensure_ascii=False, indent=2)
    return f"""const MOCK = {mock_json};

const REAL_API_BASE = "{REAL_API_BASE}";

// CORS-хедеры добавляются ко всем ответам — и mock, и проксированным.
// Без них браузер (Swagger UI на github.io) заблокирует ответ.
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

// Проксируем запрос на реальный API.
// Authorization пробрасывается из оригинального запроса (Bearer токен юзера).
// Origin/Referer/User-Agent подставляем принудительно — без них API вернёт 403.
// Query string (date_filter, language и т.д.) тоже пробрасываем без изменений.
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
    // GET-запросы не имеют body — передаём только для POST
    body: request.method !== "GET" ? request.body : undefined,
  }});

  const realResponse = await fetch(proxyRequest);
  const body = await realResponse.text();

  // Прокидываем реальный статус-код от API, но заменяем хедеры на наши CORS-хедеры
  return new Response(body, {{
    status: realResponse.status,
    headers: CORS_HEADERS,
  }});
}}

export default {{
  async fetch(request) {{
    // Preflight CORS запрос от браузера — отвечаем сразу без логики
    if (request.method === "OPTIONS") {{
      return new Response(null, {{ status: 204, headers: CORS_HEADERS }});
    }}

    const apiPath = normalizePath(new URL(request.url).pathname);
    const hasToken = request.headers.has("Authorization");

    // Есть Bearer токен → проксируем на реальный API (живые данные)
    if (hasToken) {{
      return proxyToRealApi(request, apiPath);
    }}

    // Нет токена → отдаём mock (анонимизированные данные)
    const payload = MOCK[apiPath];
    if (payload === undefined) {{
      return jsonResponse({{ error: "Not found", path: apiPath }}, 404);
    }}

    return jsonResponse(payload);
  }},
}};
"""


def main() -> int:
    examples = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    WORKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    WORKER_PATH.write_text(_render_worker(examples), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
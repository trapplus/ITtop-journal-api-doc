# Cloudflare Worker Mock Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить в проект генерацию и деплой Cloudflare Workers mock-сервера на основе анонимизированных примеров API.

**Architecture:** Источником данных для mock-сервера остаётся `data/examples/latest.json`, а `scripts/build_worker.py` конвертирует этот JSON в self-contained `mock/worker.js`. CI после текущего GitHub Pages deploy будет собирать worker и деплоить его через `wrangler`, а OpenAPI спек получит `servers` с URL mock-сервера.

**Tech Stack:** Python 3.12, GitHub Actions, Cloudflare Workers, Wrangler

---

### Task 1: Добавить конфиг Cloudflare Worker

**Files:**
- Create: `mock/wrangler.toml`

- [ ] **Step 1: Создать конфиг**

```toml
name = "ittop-mock"
main = "worker.js"
compatibility_date = "2025-01-01"
```

- [ ] **Step 2: Commit**

```bash
git add mock/wrangler.toml
git commit -m "feat: add wrangler config for mock worker"
```

### Task 2: Добавить builder script для worker

**Files:**
- Create: `scripts/build_worker.py`

- [ ] **Step 1: Реализовать генератор**

```python
def main() -> int:
    examples = json.loads(Path("data/examples/latest.json").read_text(encoding="utf-8"))
    worker_source = render_worker(examples)
    Path("mock/worker.js").write_text(worker_source, encoding="utf-8")
    return 0
```

- [ ] **Step 2: Поддержать CORS и path routing**

```javascript
const rawPath = new URL(request.url).pathname;
const path = rawPath.startsWith("/api/v2/") ? rawPath.slice("/api/v2".length) : rawPath;
```

- [ ] **Step 3: Commit**

```bash
git add scripts/build_worker.py
git commit -m "feat: add worker builder for mock api responses"
```

### Task 3: Игнорировать сгенерированный worker artifact

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Добавить ignore rule**

```gitignore
mock/worker.js
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: ignore generated mock worker artifact"
```

### Task 4: Добавить deploy шаги в GitHub Actions

**Files:**
- Modify: `.github/workflows/collect.yml`

- [ ] **Step 1: Добавить build/deploy после GitHub Pages шага**

```yaml
      - name: Build mock worker
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
        run: python scripts/build_worker.py

      - name: Deploy mock worker
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
        working-directory: mock
        run: npx wrangler deploy
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/collect.yml
git commit -m "feat: deploy mock worker from collect workflow"
```

### Task 5: Добавить mock server в OpenAPI spec

**Files:**
- Modify: `src/publisher/builder.py`

- [ ] **Step 1: Добавить `servers` в spec**

```python
"servers": [
    {
        "url": "https://ittop-mock.blazer19092008.workers.dev/api/v2",
        "description": "Mock server (anonymized data, updated daily)",
    }
],
```

- [ ] **Step 2: Commit**

```bash
git add src/publisher/builder.py
git commit -m "feat: add mock server url to openapi spec"
```

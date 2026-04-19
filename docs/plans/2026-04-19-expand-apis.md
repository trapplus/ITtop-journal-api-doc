# Journal API Discovery & Enrichment Plan

> **Scope:** New endpoints discovered and integrated into collector.

**Goal:** Expand endpoint coverage by adding working API paths from traffic analysis.

**Tech Stack:** Python 3.13, `httpx`, `dataclasses`

---

### Task 1: Add new endpoints to registry

**Files:**
- Modify: `src/collector/endpoints.py`

- [ ] **Step 1: Add new working endpoints**

```python
ENDPOINTS: list[Endpoint] = [
    # Existing endpoints...
    
    # ── New: Profile & Settings ──
    Endpoint(path="/profile/operations/settings", method="GET"),
    Endpoint(path="/profile/statistic/student-achievements", method="GET"),
    
    # ── New: News ──
    Endpoint(path="/news/operations/latest-news", method="GET"),
    
    # ── New: Localization ──
    Endpoint(path="/public/languages", method="GET"),
    Endpoint(path="/public/translations", method="GET", params={"language": "ru"}),
    
    # ── New: Library (with params) ──
    Endpoint(path="/library/operations/list", method="GET", params={
        "material_type": 2, "filter_type": 0, "recommended_type": 0
    }),
    Endpoint(path="/library/quiz/opened-interview", method="GET"),
    
    # ── New: Signals ──
    Endpoint(path="/signal/operations/signals-list", method="GET"),
    Endpoint(path="/signal/operations/problems-list", method="GET"),
    
    # ── New: Story ──
    Endpoint(path="/story/operations/get-stories", method="GET"),
]
```

- [ ] **Step 2: Commit**

```bash
git add src/collector/endpoints.py
git commit -m "feat: add new working endpoints from discovery"
```

---

### Task 2: Verify collection

**Files:**
- Read: `client.py`, `latest.json`

- [ ] **Step 1: Run collector and check output**

```bash
uv run main.py
# Expected: PIPELINE_OK, new keys in latest.json
```

- [ ] **Step 2: Confirm new data present**

```bash
jq 'keys' latest.json
# Should include: /profile/operations/settings, /news/operations/latest-news, etc.
```

- [ ] **Step 3: Commit**

```bash
git add latest.json
git commit -m "chore: verify new endpoints collected successfully"
```

---

### Excluded endpoints (reason)

| Endpoint | Reason |
|----------|--------|
| `/vacancy/*` | 410 Gone — removed on server |
| `/payment/*` | Sensitive, per user request |
| `/contacts/mailing/*` | Requires dynamic code/token |
| `/library/operations/check-url` | 405 Method Not Allowed |
| `/signal/operations/get-reference-status` | Empty response, needs dynamic params |
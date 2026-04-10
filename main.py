"""Pipeline entrypoint for collection, validation, anonymization, and publishing."""

import asyncio
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

from src.anonymizer.anonymizer import Anonymizer
from src.collector.client import JournalClient
from src.collector.endpoints import ENDPOINTS
from src.publisher.builder import OpenAPIBuilder
from src.validator.validator import Validator

VALIDATION_FAILED_MARKER = "VALIDATION_FAILED"
PIPELINE_OK_MARKER = "PIPELINE_OK"


def _write_json(path: Path, payload: Any) -> None:
    """Write JSON payload to disk with UTF-8 formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_error_report(action: str, error_message: str, tb: str) -> None:
    """Write a structured error report for manual troubleshooting."""

    report_path = Path("data/error_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = (
        "# Pipeline Error Report\n\n"
        f"## Action\n{action}\n\n"
        f"## Error\n```text\n{error_message}\n```\n\n"
        "## Traceback\n"
        f"```text\n{tb}\n```\n"
    )
    report_path.write_text(report, encoding="utf-8")


async def run_pipeline() -> None:
    """Execute the full collection-to-publication pipeline."""

    login = os.environ["JOURNAL_LOGIN"]
    password = os.environ["JOURNAL_PASSWORD"]

    client = JournalClient(login, password)
    try:
        raw = await client.collect_all(ENDPOINTS)
    finally:
        await client.close()

    _write_json(Path("data/raw/latest.json"), raw)

    validator = Validator()
    results = validator.validate_all(raw)
    if validator.has_failures(results):
        issue_body = validator.format_issue_body(results)
        Path("data/validation_issue.md").write_text(issue_body, encoding="utf-8")
        print(VALIDATION_FAILED_MARKER)

    anonymizer = Anonymizer()
    clean = anonymizer.anonymize(raw)
    _write_json(Path("data/examples/latest.json"), clean)

    is_api_down = bool(raw) and all(isinstance(item, dict) and "error" in item for item in raw.values())

    builder = OpenAPIBuilder()
    spec = builder.build(examples=clean, is_api_down=is_api_down)
    builder.save(spec)

    print(PIPELINE_OK_MARKER)


def main() -> int:
    """Run async pipeline and report structured errors on failure."""

    try:
        asyncio.run(run_pipeline())
    except Exception as error:  # noqa: BLE001
        tb = traceback.format_exc()
        print(tb, file=sys.stdout)
        _write_error_report("running pipeline", str(error), tb)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

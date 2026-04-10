"""Validator module: validates raw API responses against Pydantic models."""

import logging
from dataclasses import dataclass, field
from typing import Any

from .models import (
    UserInfoResponse,
    AverageProgressItem,
    AttendanceItem,
    LeaderboardItem,
    StudentVisitItem,
    HomeworkCountItem,
    ScheduleItem,
    ReviewItem,
    EvaluateLessonItem,
    PublicTagItem,
)

LOGGER = logging.getLogger(__name__)

# Map: endpoint path -> (model, is_list)
MODELS: dict[str, tuple[type, bool]] = {
    "/settings/user-info":                        (UserInfoResponse,    False),
    "/dashboard/chart/average-progress":          (AverageProgressItem, True),
    "/dashboard/chart/attendance":                (AttendanceItem,      True),
    "/dashboard/progress/leader-group":           (LeaderboardItem,     True),
    "/dashboard/progress/leader-stream":          (LeaderboardItem,     True),
    "/progress/operations/student-visits":        (StudentVisitItem,    True),
    "/count/homework":                            (HomeworkCountItem,   True),
    "/schedule/operations/get-by-date":           (ScheduleItem,        True),
    "/reviews/index/list":                        (ReviewItem,          True),
    "/feedback/students/evaluate-lesson-list":    (EvaluateLessonItem,  True),
    "/public/tags":                               (PublicTagItem,       True),
}


@dataclass
class ValidationResult:
    endpoint: str
    success: bool
    errors: list[str] = field(default_factory=list)


class Validator:
    def validate_all(self, raw: dict[str, Any]) -> list[ValidationResult]:
        results = []
        for path, data in raw.items():
            # 1. Обработка ошибок сетевого уровня от Collector
            if isinstance(data, dict) and "error" in data:
                results.append(ValidationResult(
                    endpoint=path,
                    success=False,
                    errors=[f"Collector Error: {data['error']}"]
                ))
                continue

            if path not in MODELS:
                results.append(ValidationResult(endpoint=path, success=True, errors=[]))
                continue

            model, is_list = MODELS[path]

            try:
                if is_list:
                    if not isinstance(data, list):
                        raise TypeError(f"Expected list, but received {type(data).__name__}")
                    for item in data:
                        model.model_validate(item)
                else:
                    if not isinstance(data, dict):
                        raise TypeError(f"Expected dict, but received {type(data).__name__}")
                    model.model_validate(data)
                
                results.append(ValidationResult(endpoint=path, success=True, errors=[]))
            except Exception as e:
                results.append(ValidationResult(endpoint=path, success=False, errors=[str(e)]))

        return results

    def has_failures(self, results: list[ValidationResult]) -> bool:
        return any(not r.success for r in results)

    def format_issue_body(self, results: list[ValidationResult]) -> str:
        lines = [
            "# API schema changed — validation failed",
            "",
            "Collected payloads do not match current validation models.",
            ""
        ]
        for r in results:
            if not r.success:
                lines.append(f"### `{r.endpoint}`")
                for e in r.errors:
                    lines.append(f"* {e}")
                lines.append("")
        return "\n".join(lines)
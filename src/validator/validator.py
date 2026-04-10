"""Validator module: validates raw API responses against Pydantic models."""

from dataclasses import dataclass, field
from typing import Any
from pydantic import ValidationError

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
            if path not in MODELS:
                results.append(ValidationResult(endpoint=path, success=True,
                                                errors=["No model defined — skipped"]))
                continue

            model, is_list = MODELS[path]

            # Skip error responses stored during collection
            if isinstance(data, dict) and "error" in data and len(data) == 1:
                results.append(ValidationResult(endpoint=path, success=False,
                                                errors=[f"Collection error: {data['error']}"]))
                continue

            errors: list[str] = []
            try:
                if is_list:
                    if not isinstance(data, list):
                        errors.append(f"Expected list, got {type(data).__name__}")
                    else:
                        for i, item in enumerate(data):
                            try:
                                model.model_validate(item)
                            except ValidationError as e:
                                for err in e.errors():
                                    errors.append(f"[{i}].{'.'.join(str(x) for x in err['loc'])}: {err['msg']}")
                else:
                    model.model_validate(data)
            except ValidationError as e:
                for err in e.errors():
                    errors.append(f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}")

            results.append(ValidationResult(endpoint=path, success=len(errors) == 0, errors=errors))

        return results

    def has_failures(self, results: list[ValidationResult]) -> bool:
        return any(not r.success for r in results)

    def format_issue_body(self, results: list[ValidationResult]) -> str:
        lines = ["# API schema changed — validation failed",
                 "",
                 "Collected payloads do not match current validation models.",
                 ""]
        for r in results:
            if not r.success:
                lines.append(f"`{r.endpoint}`")
                for e in r.errors:
                    lines.append(f"* {e}")
                lines.append("")
        return "\n".join(lines)
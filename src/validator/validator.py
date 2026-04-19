"""API response validator using Pydantic models."""

from dataclasses import dataclass, field
from typing import Any

from .models import (
    # existing models
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
    # new models
    ProfileSettingsResponse,
    StudentAchievementItem,
    ChartProgressItem,
    ActivityItem,
    LeaderPointsResponse,
    FutureExamItem,
    StudentExamItem,
    LibraryItem,
    SocialReviewItem,
    SignalItem,
    ProblemItem,
    NewsItem,
    LanguageItem,
    PublicTranslationsResponse,
)


@dataclass
class ValidationResult:
    """Result of validation for a single endpoint."""

    endpoint: str
    success: bool
    errors: list[str] = field(default_factory=list)


# Mapping of endpoint paths to (model_class, is_list) tuples
MODELS: dict[str, tuple[type, bool]] = {
    "/settings/user-info":                              (UserInfoResponse,         False),
    "/profile/operations/settings":                     (ProfileSettingsResponse,   False),
    "/profile/statistic/student-achievements":          (StudentAchievementItem,    True),
    "/dashboard/chart/average-progress":                (AverageProgressItem,       True),
    "/dashboard/chart/attendance":                      (AttendanceItem,            True),
    "/dashboard/chart/progress":                        (ChartProgressItem,         True),
    "/dashboard/progress/activity":                     (ActivityItem,              True),
    "/dashboard/progress/leader-group":                 (LeaderboardItem,           True),
    "/dashboard/progress/leader-stream":                (LeaderboardItem,           True),
    "/dashboard/progress/leader-group-points":          (LeaderPointsResponse,      False),
    "/dashboard/progress/leader-stream-points":         (LeaderPointsResponse,      False),
    "/dashboard/info/future-exams":                     (FutureExamItem,            True),
    "/schedule/operations/get-by-date-range":           (ScheduleItem,              True),
    "/schedule/operations/get-month":                   (ScheduleItem,              True),
    "/progress/operations/student-visits":              (StudentVisitItem,          True),
    "/progress/operations/student-exams":               (StudentExamItem,           True),
    "/library/operations/list":                         (LibraryItem,               True),
    "/count/homework":                                  (HomeworkCountItem,         True),
    "/reviews/index/list":                              (ReviewItem,                True),
    "/feedback/students/evaluate-lesson-list":          (EvaluateLessonItem,        True),
    "/feedback/social-review/get-review-list":          (SocialReviewItem,          True),
    "/signal/operations/signals-list":                  (SignalItem,                True),
    "/signal/operations/problems-list":                 (ProblemItem,               True),
    "/news/operations/latest-news":                     (NewsItem,                  True),
    "/public/languages":                                (LanguageItem,              True),
    "/public/translations":                             (PublicTranslationsResponse, False),
    "/public/tags":                                     (PublicTagItem,             True),
}


class Validator:
    """Validates API responses against Pydantic models."""

    @staticmethod
    def validate_all(responses: dict[str, Any]) -> list[ValidationResult]:
        """
        Validate all API responses against their corresponding models.

        Args:
            responses: Dictionary mapping endpoint paths to response data.

        Returns:
            List of ValidationResult objects for each endpoint.
        """
        results: list[ValidationResult] = []

        for path, data in responses.items():
            # Check for error response
            if isinstance(data, dict) and "error" in data:
                results.append(ValidationResult(
                    endpoint=path,
                    success=False,
                    errors=[f"API returned error: {data.get('error')}"]
                ))
                continue

            # Null response — consider valid (API returned null intentionally)
            if data is None:
                results.append(ValidationResult(endpoint=path, success=True, errors=[]))
                continue

            if path not in MODELS:
                results.append(ValidationResult(
                    endpoint=path,
                    success=True,
                    errors=[]  # Unknown endpoint, skip validation
                ))
                continue

            model_class, is_list = MODELS[path]

            try:
                if is_list:
                    if not isinstance(data, list):
                        results.append(ValidationResult(
                            endpoint=path,
                            success=False,
                            errors=[f"Expected list, got {type(data).__name__}"]
                        ))
                        continue
                    # Validate each item in the list
                    for i, item in enumerate(data):
                        model_class.model_validate(item)
                else:
                    if not isinstance(data, dict):
                        results.append(ValidationResult(
                            endpoint=path,
                            success=False,
                            errors=[f"Expected dict, got {type(data).__name__}"]
                        ))
                        continue
                    model_class.model_validate(data)

                results.append(ValidationResult(endpoint=path, success=True, errors=[]))

            except Exception as e:
                results.append(ValidationResult(
                    endpoint=path,
                    success=False,
                    errors=[str(e)]
                ))

        return results

"""Pydantic placeholder models for known Journal API endpoints."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class UserInfoResponse(BaseModel):
    """Model for /settings/user-info."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    id: int | None = None
    name: str | None = None
    email: str | None = None


class AverageProgressResponse(BaseModel):
    """Model for /dashboard/chart/average-progress."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    average: float | None = None
    points: list[dict[str, Any]] | None = None


class AttendanceChartResponse(BaseModel):
    """Model for /dashboard/chart/attendance."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    attendance: float | None = None
    timeline: list[dict[str, Any]] | None = None


class LeaderGroupProgressResponse(BaseModel):
    """Model for /dashboard/progress/leader-group."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    leaders: list[dict[str, Any]] | None = None


class LeaderStreamProgressResponse(BaseModel):
    """Model for /dashboard/progress/leader-stream."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    leaders: list[dict[str, Any]] | None = None


class StudentVisitsResponse(BaseModel):
    """Model for /progress/operations/student-visits."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    visits: list[dict[str, Any]] | None = None


class HomeworkCountResponse(BaseModel):
    """Model for /count/homework."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    count: int | None = None


class ScheduleByDateResponse(BaseModel):
    """Model for /schedule/operations/get-by-date."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    date: str | None = None
    lessons: list[dict[str, Any]] | None = None


class ReviewsListResponse(BaseModel):
    """Model for /reviews/index/list."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    reviews: list[dict[str, Any]] | None = None


class EvaluateLessonListResponse(BaseModel):
    """Model for /feedback/students/evaluate-lesson-list."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    lessons: list[dict[str, Any]] | None = None


class PublicTagsResponse(BaseModel):
    """Model for /public/tags."""

    model_config = ConfigDict(extra="allow")
    # TODO: update fields after first real collection run
    tags: list[str] | list[dict[str, Any]] | None = None


MODELS: dict[str, type[BaseModel]] = {
    "/settings/user-info": UserInfoResponse,
    "/dashboard/chart/average-progress": AverageProgressResponse,
    "/dashboard/chart/attendance": AttendanceChartResponse,
    "/dashboard/progress/leader-group": LeaderGroupProgressResponse,
    "/dashboard/progress/leader-stream": LeaderStreamProgressResponse,
    "/progress/operations/student-visits": StudentVisitsResponse,
    "/count/homework": HomeworkCountResponse,
    "/schedule/operations/get-by-date": ScheduleByDateResponse,
    "/reviews/index/list": ReviewsListResponse,
    "/feedback/students/evaluate-lesson-list": EvaluateLessonListResponse,
    "/public/tags": PublicTagsResponse,
}

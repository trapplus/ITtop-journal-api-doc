"""Pydantic models for API response validation."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    """Base model with extra fields allowed."""

    model_config = ConfigDict(extra="allow")


# =============================================================================
# /settings/user-info
# =============================================================================
class UserInfoResponse(_Base):
    """Response model for /settings/user-info endpoint."""

    id: int | None = None
    name: str | None = None
    email: str | None = None
    # groups, gaming_points, spent_gaming_points, visibility covered by extra="allow"


# =============================================================================
# /profile/operations/settings
# =============================================================================
class ProfilePhoneItem(_Base):
    """Phone item in profile settings."""

    phone_type: int | None = None
    phone_number: str | None = None


class ProfileLinkItem(_Base):
    """Link item in profile settings."""

    id: int | None = None
    name: str | None = None
    reg: str | None = None
    required_type: int | None = None
    value: Any = None
    valid: bool | None = None
    is_required: bool | None = None
    show_link: bool | None = None


class ProfileAzure(_Base):
    """Azure info in profile settings."""

    login: str | None = None
    has_azure: bool | None = None
    has_office: bool | None = None


class ProfileSettingsResponse(_Base):
    """Response model for /profile/operations/settings endpoint."""

    id: int | None = None
    ful_name: str | None = None   # typo in API — intentional
    address: str | None = None
    date_birth: str | None = None
    study: str | None = None
    email: str | None = None
    last_approving_status: int | None = None
    form_type: int | None = None
    photo_path: str | None = None
    has_not_approved_data: bool | None = None
    has_not_approved_photo: bool | None = None
    is_email_verified: bool | None = None
    is_phone_verified: bool | None = None
    phones: list[Any] = []
    links: list[Any] = []
    relatives: list[Any] = []
    fill_percentage: int | None = None
    decline_comment: Any = None
    azure: Any = None
    azure_login: Any = None


# =============================================================================
# /profile/statistic/student-achievements
# =============================================================================
class AchievePointItem(_Base):
    """Achievement point item."""

    id: int | None = None
    points_count: int | None = None


class StudentAchievementItem(_Base):
    """Student achievement item."""

    id: int | None = None
    translate_key: str | None = None
    is_active: bool | None = None
    achieve_points: list[Any] = []


# =============================================================================
# /dashboard/chart/progress
# =============================================================================
class ChartModelItem(_Base):
    """Chart model item."""

    date: str | None = None
    points: int | float | None = None
    previous_points: int | float | None = None
    has_rasp: bool | None = None


class ChartProgressItem(_Base):
    """Chart progress item."""

    chart_type: int | None = None
    chart_models: list[Any] = []


# =============================================================================
# /dashboard/progress/activity
# =============================================================================
class ActivityItem(_Base):
    """Activity item."""

    date: str | None = None
    action: int | None = None
    current_point: int | None = None
    point_types_id: int | None = None
    point_types_name: str | None = None
    achievements_id: int | None = None
    achievements_name: str | None = None
    achievements_type: int | None = None
    badge: int | None = None
    old_competition: bool | None = None


# =============================================================================
# /dashboard/progress/leader-group-points and leader-stream-points
# =============================================================================
class LeaderPointsResponse(_Base):
    """Leader points response."""

    totalCount: int | None = None
    studentPosition: int | None = None
    weekDiff: int | None = None
    monthDiff: int | None = None


# =============================================================================
# /dashboard/info/future-exams
# =============================================================================
class FutureExamItem(_Base):
    """Future exam item."""

    spec: str | None = None
    date: str | None = None


# =============================================================================
# /schedule/operations/get-month and get-by-date-range
# Reusing ScheduleItem (already defined below)
# =============================================================================
class ScheduleItem(_Base):
    """Schedule item."""

    id: int | None = None
    date: str | None = None
    time: str | None = None
    subject: str | None = None
    teacher: str | None = None
    room: str | None = None


# =============================================================================
# /progress/operations/student-exams
# =============================================================================
class StudentExamItem(_Base):
    """Student exam item."""

    teacher: str | None = None
    mark: int | float | None = None
    mark_type: int | None = None
    date: str | None = None
    ex_file_name: Any = None
    id_file: int | None = None
    exam_id: int | None = None
    file_path: str | None = None
    comment_teach: str | None = None
    need_access: int | None = None
    need_access_stud: Any = None
    comment_delete_file: Any = None
    spec: str | None = None


# =============================================================================
# /library/operations/list
# =============================================================================
class LibraryItem(_Base):
    """Library item (passthrough model)."""

    pass


# =============================================================================
# /feedback/social-review/get-review-list
# =============================================================================
class SocialReviewItem(_Base):
    """Social review item."""

    status: Any = None
    social_id: int | None = None
    link_id: Any = None
    link: str | None = None
    screen_shot: str | None = None
    review_id: Any = None
    comment: str | None = None
    teach_name: str | None = None
    updated_at: str | None = None
    is_visibility: bool | None = None


# =============================================================================
# /signal/operations/signals-list
# =============================================================================
class SignalItem(_Base):
    """Signal item."""

    id: int | None = None
    date_desired: str | None = None
    date_start: str | None = None
    priority: int | None = None
    status: int | None = None
    message: str | None = None
    initiator_name: str | None = None
    problem_id: int | None = None
    problem_name: str | None = None
    problem_type: int | None = None
    days_diff: int | None = None
    theme: str | None = None


# =============================================================================
# /signal/operations/problems-list
# =============================================================================
class ProblemItem(_Base):
    """Problem item."""

    id: int | None = None
    title: str | None = None


# =============================================================================
# /news/operations/latest-news
# =============================================================================
class NewsItem(_Base):
    """News item."""

    id_bbs: int | None = None
    theme: str | None = None
    time: str | None = None
    viewed: bool | None = None


# =============================================================================
# /public/languages
# =============================================================================
class LanguageItem(_Base):
    """Language item."""

    name_mystat: str | None = None
    short_name: str | None = None


# =============================================================================
# /public/translations
# =============================================================================
class PublicTranslationsResponse(_Base):
    """Public translations response (flat key:value string mapping)."""

    pass


# =============================================================================
# Existing models from original code
# =============================================================================
class AverageProgressItem(_Base):
    """Average progress item."""

    date: str | None = None
    average: int | float | None = None


class AttendanceItem(_Base):
    """Attendance item."""

    date: str | None = None
    visited: int | None = None
    total: int | None = None


class LeaderboardItem(_Base):
    """Leaderboard item."""

    position: int | None = None
    student_id: int | None = None
    student_name: str | None = None
    points: int | float | None = None


class StudentVisitItem(_Base):
    """Student visit item."""

    date: str | None = None
    status: int | None = None


class HomeworkCountItem(_Base):
    """Homework count item."""

    subject: str | None = None
    count: int | None = None


class ReviewItem(_Base):
    """Review item."""

    id: int | None = None
    rating: int | None = None
    comment: str | None = None
    created_at: str | None = None


class EvaluateLessonItem(_Base):
    """Evaluate lesson item."""

    lesson_id: int | None = None
    rating: int | None = None
    comment: str | None = None


class PublicTagItem(_Base):
    """Public tag item."""

    id: int | None = None
    name: str | None = None

"""Pydantic v2 models for IT Top Journal API endpoints."""

from pydantic import BaseModel, ConfigDict
from typing import Any


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow")


# ── /settings/user-info — dict ─────────────────────────────────────────────

class UserInfoResponse(_Base):
    student_id: int | None = None
    full_name: str | None = None
    group_name: str | None = None
    stream_name: str | None = None
    level: int | None = None
    age: int | None = None
    gender: int | None = None
    birthday: str | None = None
    last_date_visit: str | None = None
    registration_date: str | None = None
    current_group_id: int | None = None
    current_group_status: int | None = None
    stream_id: int | None = None
    achieves_count: int | None = None
    manual_link: Any = None
    photo: str | None = None
    study_form_short_name: str | None = None
    # gaming_points, spent_gaming_points, visibility, groups — не критичные поля,
    # extra="allow" подхватит их автоматически


# ── /profile/operations/settings — dict ───────────────────────────────────

class ProfileSettingsResponse(_Base):
    id: int | None = None
    # Опечатка в оригинальном API: "ful_name" вместо "full_name" — сохраняем как есть
    ful_name: str | None = None
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
    fill_percentage: int | float | None = None
    decline_comment: Any = None
    azure_login: Any = None
    # phones, links, relatives, azure — вложенные объекты,
    # extra="allow" покрывает их без отдельных подмоделей


# ── /profile/statistic/student-achievements — list ────────────────────────

class AchievementItem(_Base):
    id: int | None = None
    translate_key: str | None = None
    is_active: bool | None = None
    # achieve_points — вложенный список [{id, points_count}],
    # описываем как Any чтобы не плодить лишние модели
    achieve_points: list[Any] | None = None


# ── /dashboard/chart/average-progress — list ──────────────────────────────

class AverageProgressItem(_Base):
    date: str | None = None
    points: int | float | None = None
    previous_points: int | float | None = None
    has_rasp: bool | None = None


# ── /dashboard/chart/attendance — list ────────────────────────────────────

class AttendanceItem(_Base):
    date: str | None = None
    points: int | float | None = None
    previous_points: int | float | None = None
    has_rasp: bool | None = None


# ── /dashboard/chart/progress — list ──────────────────────────────────────
# Возвращает список объектов, каждый из которых содержит chart_type (int)
# и chart_models (список с той же структурой что и AverageProgressItem).
# chart_models валидируем как list[Any] — дополнительная валидация вложенных
# данных уже покрыта тестами AverageProgressItem/AttendanceItem.

class ChartProgressItem(_Base):
    chart_type: int | None = None
    chart_models: list[Any] | None = None


# ── /dashboard/progress/activity — list ───────────────────────────────────

class ActivityItem(_Base):
    date: str | None = None
    action: int | None = None
    current_point: int | float | None = None
    point_types_id: int | None = None
    point_types_name: str | None = None
    achievements_id: int | None = None
    achievements_name: str | None = None
    achievements_type: int | None = None
    badge: int | None = None
    old_competition: bool | None = None


# ── /dashboard/progress/leader-group — list ───────────────────────────────
# ── /dashboard/progress/leader-stream — list ──────────────────────────────

class LeaderboardItem(_Base):
    id: int | None = None
    full_name: str | None = None
    photo_path: str | None = None
    position: int | None = None
    amount: int | float | None = None


# ── /dashboard/progress/leader-group-points — dict ────────────────────────
# ── /dashboard/progress/leader-stream-points — dict ───────────────────────
# Оба эндпоинта возвращают одинаковую структуру — используем одну модель.
# totalCount может быть null (замечено в leader-stream-points из датасета).

class LeaderPointsResponse(_Base):
    totalCount: int | None = None
    studentPosition: int | None = None
    weekDiff: int | float | None = None
    monthDiff: int | float | None = None


# ── /dashboard/info/future-exams — list ───────────────────────────────────

class FutureExamItem(_Base):
    spec: str | None = None
    date: str | None = None


# ── /dashboard/progress/leader-group — list (уже выше) ───────────────────
# ── /dashboard/progress/leader-stream — list (уже выше) ──────────────────

# ── /schedule/operations/get-by-date-range — list ─────────────────────────
# ── /schedule/operations/get-month — list ─────────────────────────────────
# ── (старый путь /get-by-date был багом — в MODELS его не будет) ───────────
# Все три schedule-эндпоинта возвращают одинаковую структуру — один класс.

class ScheduleItem(_Base):
    date: str | None = None
    lesson: int | None = None
    started_at: str | None = None
    finished_at: str | None = None
    teacher_name: str | None = None
    subject_name: str | None = None
    room_name: str | None = None


# ── /progress/operations/student-visits — list ────────────────────────────

class StudentVisitItem(_Base):
    date_visit: str | None = None
    lesson_number: int | None = None
    status_was: int | None = None
    spec_id: int | None = None
    teacher_name: str | None = None
    spec_name: str | None = None
    lesson_theme: str | None = None
    control_work_mark: int | float | None = None
    home_work_mark: int | float | None = None
    lab_work_mark: int | float | None = None
    class_work_mark: int | float | None = None
    practical_work_mark: int | float | None = None
    final_work_mark: int | float | None = None


# ── /progress/operations/student-exams — list ─────────────────────────────

class StudentExamItem(_Base):
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


# ── /count/homework — list ────────────────────────────────────────────────

class HomeworkCountItem(_Base):
    counter_type: int | None = None
    counter: int | None = None


# ── /library/operations/list — list ───────────────────────────────────────
# В датасете вернул пустой список — структура элементов неизвестна.
# Используем пустую модель с extra="allow" чтобы не падать когда данные появятся.

class LibraryItem(_Base):
    pass


# ── /reviews/index/list — list ────────────────────────────────────────────

class ReviewItem(_Base):
    date: str | None = None
    message: str | None = None
    spec: str | None = None
    full_spec: str | None = None
    teacher: str | None = None


# ── /feedback/students/evaluate-lesson-list — list ────────────────────────

class EvaluateLessonItem(_Base):
    key: str | None = None
    date_visit: str | None = None
    fio_teach: str | None = None
    spec_name: str | None = None
    teach_photo: Any = None


# ── /feedback/social-review/get-review-list — list ────────────────────────

class SocialReviewItem(_Base):
    status: Any = None
    social_id: int | None = None
    link_id: int | None = None
    link: str | None = None
    screen_shot: str | None = None
    review_id: int | None = None
    comment: str | None = None
    teach_name: str | None = None
    updated_at: str | None = None
    is_visibility: bool | None = None


# ── /signal/operations/signals-list — list ────────────────────────────────

class SignalItem(_Base):
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


# ── /signal/operations/problems-list — list ───────────────────────────────

class ProblemItem(_Base):
    id: int | None = None
    title: str | None = None


# ── /news/operations/latest-news — list ───────────────────────────────────

class NewsItem(_Base):
    id_bbs: int | None = None
    theme: str | None = None
    time: str | None = None
    viewed: bool | None = None


# ── /public/languages — list ──────────────────────────────────────────────

class LanguageItem(_Base):
    name_mystat: str | None = None
    short_name: str | None = None


# ── /public/translations — dict ───────────────────────────────────────────
# Огромный словарь строка→строка (локализационные ключи).
# extra="allow" поглощает все ключи без явного перечисления.
# Отдельные поля не фиксируем — их тысячи и они не несут структурной ценности.

class TranslationsResponse(_Base):
    pass


# ── /public/tags — list ───────────────────────────────────────────────────
# В датасете пустой список — структура неизвестна, аналогично LibraryItem.

class PublicTagItem(_Base):
    pass
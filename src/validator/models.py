"""Pydantic v2 models for IT Top Journal API endpoints."""

from pydantic import BaseModel, ConfigDict
from typing import Any


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow")


# /settings/user-info — dict
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


# /dashboard/chart/average-progress — list of these
class AverageProgressItem(_Base):
    date: str | None = None
    points: int | float | None = None
    previous_points: int | float | None = None
    has_rasp: bool | None = None


# /dashboard/chart/attendance — list of these
class AttendanceItem(_Base):
    date: str | None = None
    points: int | float | None = None
    previous_points: int | float | None = None
    has_rasp: bool | None = None


# /dashboard/progress/leader-group and leader-stream — list of these
class LeaderboardItem(_Base):
    id: int | None = None
    full_name: str | None = None
    photo_path: str | None = None
    position: int | None = None
    amount: int | float | None = None


# /progress/operations/student-visits — list of these
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


# /count/homework — list of these
class HomeworkCountItem(_Base):
    counter_type: int | None = None
    counter: int | None = None


# /schedule/operations/get-by-date — list of these
class ScheduleItem(_Base):
    date: str | None = None
    lesson: int | None = None
    started_at: str | None = None
    finished_at: str | None = None
    teacher_name: str | None = None
    subject_name: str | None = None
    room_name: str | None = None


# /reviews/index/list — list of these
class ReviewItem(_Base):
    date: str | None = None
    message: str | None = None
    spec: str | None = None
    full_spec: str | None = None
    teacher: str | None = None


# /feedback/students/evaluate-lesson-list — list of these
class EvaluateLessonItem(_Base):
    key: str | None = None
    date_visit: str | None = None
    fio_teach: str | None = None
    spec_name: str | None = None
    teach_photo: Any = None


# /public/tags — list (empty or items with unknown structure)
class PublicTagItem(_Base):
    pass
from dataclasses import dataclass
from datetime import date

BASE_API_URL = "https://msapi.top-academy.ru/api/v2"
LOGIN_PATH = "/auth/login"

@dataclass(slots=True, frozen=True)
class Endpoint:
    path: str
    method: str
    params: dict | None = None

ENDPOINTS: list[Endpoint] = [
    Endpoint(path=LOGIN_PATH, method="POST", params={
        "application_key": "6a56a5df2667e65aab73ce76d1dd737f7d1faef9c52e8b8c55ac75f565d8e8a6",
        "id_city": None,
        "username": "<login>",
        "password": "<password>",
    }),
    Endpoint(path="/settings/user-info", method="GET"),
    Endpoint(path="/profile/operations/settings", method="GET"),
    Endpoint(path="/profile/statistic/student-achievements", method="GET"),
    Endpoint(path="/dashboard/chart/average-progress", method="GET"),
    Endpoint(path="/dashboard/chart/attendance", method="GET"),
    Endpoint(path="/dashboard/chart/progress", method="GET"),
    Endpoint(path="/dashboard/progress/activity", method="GET"),
    Endpoint(path="/dashboard/progress/leader-group", method="GET"),
    Endpoint(path="/dashboard/progress/leader-stream", method="GET"),
    Endpoint(path="/dashboard/progress/leader-group-points", method="GET"),
    Endpoint(path="/dashboard/progress/leader-stream-points", method="GET"),
    Endpoint(path="/dashboard/info/future-exams", method="GET"),
    Endpoint(path="/schedule/operations/get-by-date-range", method="GET", params={
        "date_start": date.today().isoformat(),
        "date_end": date.today().isoformat(),
    }),
    Endpoint(path="/schedule/operations/get-month", method="GET", params={
        "date_filter": date.today().isoformat(),
    }),
    Endpoint(path="/progress/operations/student-visits", method="GET"),
    Endpoint(path="/progress/operations/student-exams", method="GET"),
    Endpoint(path="/library/operations/list", method="GET", params={
        "material_type": 2,
        "filter_type": 0,
        "recommended_type": 0,
    }),
    Endpoint(path="/library/quiz/opened-interview", method="GET"),
    Endpoint(path="/count/homework", method="GET"),
    Endpoint(path="/reviews/index/list", method="GET"),
    Endpoint(path="/reviews/index/instruction", method="GET"),
    Endpoint(path="/feedback/students/evaluate-lesson-list", method="GET"),
    Endpoint(path="/feedback/social-review/get-review-list", method="GET"),
    Endpoint(path="/signal/operations/signals-list", method="GET"),
    Endpoint(path="/signal/operations/problems-list", method="GET"),
    Endpoint(path="/news/operations/latest-news", method="GET"),
    Endpoint(path="/public/languages", method="GET"),
    Endpoint(path="/public/translations", method="GET", params={"language": "ru"}),
    Endpoint(path="/public/tags", method="GET"),
]
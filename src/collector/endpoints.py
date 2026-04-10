"""Known Journal API endpoints used by the collection pipeline."""

from dataclasses import dataclass
from datetime import date

BASE_API_URL = "https://msapi.top-academy.ru/api/v2"
LOGIN_PATH = "/auth/login"


@dataclass(slots=True, frozen=True)
class Endpoint:
    """Endpoint descriptor for collector requests."""

    path: str
    method: str
    params: dict | None = None


ENDPOINTS: list[Endpoint] = [
    Endpoint(
        path=LOGIN_PATH,
        method="POST",
        params={
            "application_key": "",
            "id_city": None,
            "login": "<login>",
            "password": "<password>",
        },
    ),
    Endpoint(path="/settings/user-info", method="GET"),
    Endpoint(path="/dashboard/chart/average-progress", method="GET"),
    Endpoint(path="/dashboard/chart/attendance", method="GET"),
    Endpoint(path="/dashboard/progress/leader-group", method="GET"),
    Endpoint(path="/dashboard/progress/leader-stream", method="GET"),
    Endpoint(path="/progress/operations/student-visits", method="GET"),
    Endpoint(path="/count/homework", method="GET"),
    Endpoint(
        path="/schedule/operations/get-by-date",
        method="GET",
        params={"date": date.today().isoformat()},
    ),
    Endpoint(path="/reviews/index/list", method="GET"),
    Endpoint(path="/feedback/students/evaluate-lesson-list", method="GET"),
    Endpoint(path="/public/tags", method="GET"),
]

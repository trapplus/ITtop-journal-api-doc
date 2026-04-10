"""Field replacement rules for anonymizing sensitive values."""

from typing import Callable

from faker import Faker

fake = Faker()

RULES: dict[str, Callable[[], object]] = {
    "fio": lambda: fake.name(),
    "name": lambda: fake.name(),
    "full_name": lambda: fake.name(),
    "email": lambda: fake.email(),
    "phone": lambda: fake.phone_number(),
    "id": lambda: fake.random_int(10000, 99999),
    "student_id": lambda: fake.random_int(10000, 99999),
    "group_id": lambda: fake.random_int(100, 999),
    "login": lambda: fake.user_name(),
    "created_at": lambda: fake.iso8601(),
    "updated_at": lambda: fake.iso8601(),
    "date": lambda: fake.date(),
    "token": lambda: fake.sha256(),
    "access_token": lambda: fake.sha256(),
}

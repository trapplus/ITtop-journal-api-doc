"""Tests for the validator module."""

import pytest

from src.validator.validator import Validator, ValidationResult
from src.validator.models import (
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


class TestProfileSettingsResponse:
    """Tests for ProfileSettingsResponse model."""

    def test_valid_response(self):
        data = {
            "id": 1,
            "ful_name": "John Doe",
            "email": "john@example.com",
            "phones": [],
            "links": [],
            "relatives": [],
        }
        model = ProfileSettingsResponse.model_validate(data)
        assert model.id == 1
        assert model.ful_name == "John Doe"

    def test_extra_fields_allowed(self):
        data = {
            "id": 1,
            "ful_name": "John Doe",
            "extra_field": "should be allowed",
            "another_extra": 123,
        }
        model = ProfileSettingsResponse.model_validate(data)
        assert model.id == 1


class TestNullResponse:
    """Tests for null response handling."""

    def test_null_response_is_valid(self):
        responses = {
            "/reviews/index/instruction": None,
        }
        results = Validator.validate_all(responses)
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].errors == []


class TestStudentAchievementItem:
    """Tests for StudentAchievementItem model."""

    def test_valid_item(self):
        data = {
            "id": 1,
            "translate_key": "achievement.math",
            "is_active": True,
            "achieve_points": [{"id": 1, "points_count": 10}],
        }
        model = StudentAchievementItem.model_validate(data)
        assert model.id == 1
        assert model.translate_key == "achievement.math"


class TestChartProgressItem:
    """Tests for ChartProgressItem model."""

    def test_valid_item(self):
        data = {
            "chart_type": 1,
            "chart_models": [
                {"date": "2024-01-01", "points": 100, "previous_points": 90}
            ],
        }
        model = ChartProgressItem.model_validate(data)
        assert model.chart_type == 1


class TestActivityItem:
    """Tests for ActivityItem model."""

    def test_valid_item(self):
        data = {
            "date": "2024-01-01",
            "action": 1,
            "current_point": 100,
            "point_types_name": "Homework",
        }
        model = ActivityItem.model_validate(data)
        assert model.date == "2024-01-01"


class TestLeaderPointsResponse:
    """Tests for LeaderPointsResponse model."""

    def test_valid_response(self):
        data = {
            "totalCount": 100,
            "studentPosition": 5,
            "weekDiff": 2,
            "monthDiff": -1,
        }
        model = LeaderPointsResponse.model_validate(data)
        assert model.totalCount == 100
        assert model.studentPosition == 5


class TestFutureExamItem:
    """Tests for FutureExamItem model."""

    def test_valid_item(self):
        data = {
            "spec": "Mathematics",
            "date": "2024-06-15",
        }
        model = FutureExamItem.model_validate(data)
        assert model.spec == "Mathematics"


class TestStudentExamItem:
    """Tests for StudentExamItem model."""

    def test_valid_item(self):
        data = {
            "teacher": "Prof. Smith",
            "mark": 5,
            "mark_type": 1,
            "date": "2024-01-15",
            "spec": "Calculus",
        }
        model = StudentExamItem.model_validate(data)
        assert model.teacher == "Prof. Smith"
        assert model.mark == 5


class TestLibraryItem:
    """Tests for LibraryItem passthrough model."""

    def test_passthrough(self):
        data = {"any_field": "any_value", "another": 123}
        model = LibraryItem.model_validate(data)
        # Should accept any fields due to extra="allow"
        assert model is not None


class TestSocialReviewItem:
    """Tests for SocialReviewItem model."""

    def test_valid_item(self):
        data = {
            "social_id": 1,
            "link": "https://example.com/review",
            "comment": "Great course!",
            "is_visibility": True,
        }
        model = SocialReviewItem.model_validate(data)
        assert model.social_id == 1


class TestSignalItem:
    """Tests for SignalItem model."""

    def test_valid_item(self):
        data = {
            "id": 1,
            "priority": 2,
            "status": 1,
            "message": "Test signal",
            "theme": "Technical issue",
        }
        model = SignalItem.model_validate(data)
        assert model.id == 1


class TestProblemItem:
    """Tests for ProblemItem model."""

    def test_valid_item(self):
        data = {
            "id": 1,
            "title": "Network connectivity",
        }
        model = ProblemItem.model_validate(data)
        assert model.title == "Network connectivity"


class TestNewsItem:
    """Tests for NewsItem model."""

    def test_valid_item(self):
        data = {
            "id_bbs": 100,
            "theme": "System maintenance",
            "time": "2024-01-01T10:00:00",
            "viewed": False,
        }
        model = NewsItem.model_validate(data)
        assert model.id_bbs == 100


class TestLanguageItem:
    """Tests for LanguageItem model."""

    def test_valid_item(self):
        data = {
            "name_mystat": "English",
            "short_name": "en",
        }
        model = LanguageItem.model_validate(data)
        assert model.short_name == "en"


class TestPublicTranslationsResponse:
    """Tests for PublicTranslationsResponse model."""

    def test_flat_dict_allowed(self):
        data = {
            "LOGIN_TITLE": "Login",
            "LOGOUT_BUTTON": "Logout",
            "SETTINGS_PAGE": "Settings",
        }
        model = PublicTranslationsResponse.model_validate(data)
        # Should accept any key:value pairs
        assert model is not None


class TestValidatorIntegration:
    """Integration tests for the Validator class."""

    def test_validate_multiple_endpoints(self):
        responses = {
            "/profile/operations/settings": {"id": 1, "ful_name": "Test"},
            "/dashboard/info/future-exams": [{"spec": "Math", "date": "2024-06-01"}],
            "/public/translations": {"KEY1": "Value1"},
            "/reviews/index/instruction": None,
        }
        results = Validator.validate_all(responses)
        assert len(results) == 4
        for result in results:
            assert result.success is True, f"{result.endpoint} failed: {result.errors}"

    def test_error_response_detected(self):
        responses = {
            "/settings/user-info": {"error": "Not found"},
        }
        results = Validator.validate_all(responses)
        assert len(results) == 1
        assert results[0].success is False
        assert "error" in results[0].errors[0].lower()

import sys
sys.path.insert(0, '/workspace/src')

from validator.validator import Validator, ValidationResult, MODELS
import validator.validator as validator_module


class MockModel:
    pass


def test_unknown_path_with_error_key_is_success(monkeypatch):
    """Unknown endpoint returning {"error": ...} must NOT trigger failure."""
    monkeypatch.setattr(validator_module, "MODELS", {})
    results = Validator().validate_all({"/public/translations": {"error": "Ошибка"}})
    assert results[0].success is True


def test_known_path_with_collector_error_is_failure(monkeypatch):
    """Known endpoint returning {"error": ...} MUST trigger failure."""
    monkeypatch.setattr(validator_module, "MODELS", {"/test": (MockModel, False)})
    results = Validator().validate_all({"/test": {"error": "timeout"}})
    assert results[0].success is False
    assert "Collector Error" in results[0].errors[0]

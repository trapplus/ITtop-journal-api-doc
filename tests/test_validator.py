import pytest
from pydantic import BaseModel
from src.validator.validator import Validator, ValidationResult
import src.validator.validator as validator_module

class MockModel(BaseModel):
    id: int

def test_validate_all_for_known_path(monkeypatch):
    # Патчим MODELS так, как ожидает новый валидатор
    monkeypatch.setattr(validator_module, "MODELS", {"/test": MockModel})
    
    # 1. Успешный кейс
    results = Validator().validate_all({"/test": {"id": 1}})
    assert results[0].success is True
    
    # 2. Ошибка валидации
    results = Validator().validate_all({"/test": {"id": "not_an_int"}})
    assert results[0].success is False
    assert len(results[0].errors) > 0

def test_validate_all_unknown_path_is_success(monkeypatch):
    monkeypatch.setattr(validator_module, "MODELS", {})
    results = Validator().validate_all({"/unknown": {"any": "value"}})
    
    assert len(results) == 1
    assert results[0].success is True
    assert results[0].errors == []

def test_unknown_path_with_error_key_is_success(monkeypatch):
    monkeypatch.setattr(validator_module, "MODELS", {})
    results = Validator().validate_all({"/public/translations": {"error": "Ошибка"}})
    assert results[0].success is True

def test_known_path_with_collector_error_is_failure(monkeypatch):
    monkeypatch.setattr(validator_module, "MODELS", {"/test": (MockModel, False)})
    results = Validator().validate_all({"/test": {"error": "timeout"}})
    assert results[0].success is False
    assert "Collector Error" in results[0].errors[0]
"""Anonymizer package public interface."""

from src.anonymizer.anonymizer import Anonymizer
from src.anonymizer.rules import RULES

__all__ = ["Anonymizer", "RULES"]

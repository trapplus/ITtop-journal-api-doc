"""Collector package public interface."""

from src.collector.client import JournalClient
from src.collector.endpoints import BASE_API_URL, ENDPOINTS, Endpoint

__all__ = ["BASE_API_URL", "ENDPOINTS", "Endpoint", "JournalClient"]

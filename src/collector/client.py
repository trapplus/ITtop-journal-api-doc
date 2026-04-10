"""Async HTTP client for collecting Journal API responses."""

import asyncio
import logging
from typing import Any

import httpx

from src.collector.endpoints import BASE_API_URL, LOGIN_PATH, Endpoint

LOGGER = logging.getLogger(__name__)
RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 60
REQUEST_TIMEOUT_SECONDS = 30


class JournalClient:
    """Client that authenticates and fetches JSON responses from known endpoints."""

    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = password
        self.client = httpx.AsyncClient(
            base_url=BASE_API_URL,
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
                ),
                "Origin": "https://journal.top-academy.ru",
                "Referer": "https://journal.top-academy.ru/",
            },
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""

        await self.client.aclose()

    async def authenticate(self) -> str:
        """Authenticate and return access token."""

        payload = {
            "application_key": "",
            "id_city": None,
            "username": self.login,
            "password": self.password,
        }

        response = await self.client.post(LOGIN_PATH, json=payload)
        
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        response.raise_for_status()
        
        data = response.json()
        access_token = data.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise ValueError("Authentication response does not contain access_token.")

        self.client.headers["Authorization"] = f"Bearer {access_token}"
        return access_token

    async def fetch(self, endpoint: Endpoint) -> dict | list:
        """Request a single endpoint and return JSON response."""

        request_kwargs: dict[str, Any] = {}
        method = endpoint.method.upper()

        if method == "GET" and endpoint.params is not None:
            request_kwargs["params"] = endpoint.params
        if method == "POST" and endpoint.params is not None:
            request_kwargs["json"] = endpoint.params

        try:
            response = await self.client.request(method, endpoint.path, **request_kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            LOGGER.exception("HTTP request failed for %s %s", method, endpoint.path)
            raise

    async def _fetch_with_retry(self, endpoint: Endpoint) -> dict | list:
        """Fetch endpoint with bounded retries on failure."""

        last_error: Exception | None = None
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                return await self.fetch(endpoint)
            except Exception as error:  # noqa: BLE001
                last_error = error
                if attempt == RETRY_ATTEMPTS:
                    break

                LOGGER.warning(
                    "Retrying %s %s in %s seconds (attempt %s/%s): %s",
                    endpoint.method,
                    endpoint.path,
                    RETRY_DELAY_SECONDS,
                    attempt,
                    RETRY_ATTEMPTS,
                    error,
                )
                await asyncio.sleep(RETRY_DELAY_SECONDS)

        raise RuntimeError(
            f"Failed to fetch {endpoint.method} {endpoint.path} "
            f"after {RETRY_ATTEMPTS} attempts."
        ) from last_error

    async def collect_all(self, endpoints: list[Endpoint]) -> dict[str, Any]:
        """Collect all endpoint responses and continue on per-endpoint failures."""

        await self.authenticate()

        collected: dict[str, Any] = {}
        for endpoint in endpoints:
            if endpoint.path == LOGIN_PATH:
                continue

            try:
                collected[endpoint.path] = await self._fetch_with_retry(endpoint)
            except Exception as error:  # noqa: BLE001
                LOGGER.warning(
                    "Endpoint collection failed for %s %s: %s",
                    endpoint.method,
                    endpoint.path,
                    error,
                )
                collected[endpoint.path] = {"error": str(error)}

        return collected

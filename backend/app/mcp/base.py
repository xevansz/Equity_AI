import asyncio
import hashlib
import json
import random
import time

import httpx


class CircuitOpenError(Exception):
    """Raised when the circuit breaker is open and calls are rejected."""


class BaseMCP:
    """Base MCP Connector with TTL cache, retry/backoff, and circuit breaker."""

    # tunables (subclasses may override)
    CACHE_TTL: float = 300.0  # seconds; 0 disables caching
    MAX_RETRIES: int = 3
    BACKOFF_BASE: float = 1.0  # seconds
    BACKOFF_MAX: float = 30.0  # seconds cap
    CB_FAILURE_THRESHOLD: int = 5  # consecutive failures to open circuit
    CB_RECOVERY_TIMEOUT: float = 60.0  # seconds before half-open probe

    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self._closed = False

        # in-memory cache: key -> (payload, expiry_monotonic)
        self._cache: dict[str, tuple[object, float]] = {}

        # circuit breaker state
        self._cb_failures = 0
        self._cb_opened_at: float | None = None

    # lifecycle
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        if not self._closed:
            self._closed = True
            await self.client.aclose()

    # cache helpers
    @staticmethod
    def _cache_key(url: str, params: dict) -> str:
        canonical = json.dumps(params, sort_keys=True)
        return hashlib.sha256(f"{url}|{canonical}".encode()).hexdigest()

    def _cache_get(self, key: str) -> object | None:
        if self.CACHE_TTL <= 0:
            return None
        entry = self._cache.get(key)
        if entry is None:
            return None
        payload, expiry = entry
        if time.monotonic() > expiry:
            del self._cache[key]
            return None
        return payload

    def _cache_set(self, key: str, payload: object) -> None:
        if self.CACHE_TTL > 0:
            self._cache[key] = (payload, time.monotonic() + self.CACHE_TTL)

    # circuit breaker helpers
    def _cb_check(self) -> None:
        """Raise CircuitOpenError if the breaker is open."""
        if self._cb_opened_at is None:
            return
        elapsed = time.monotonic() - self._cb_opened_at
        if elapsed < self.CB_RECOVERY_TIMEOUT:
            raise CircuitOpenError(
                f"{self.__class__.__name__} circuit open (retry in {self.CB_RECOVERY_TIMEOUT - elapsed:.0f}s)"
            )
        # half-open: allow one probe through
        self._cb_opened_at = None

    def _cb_record_success(self) -> None:
        self._cb_failures = 0
        self._cb_opened_at = None

    def _cb_record_failure(self) -> None:
        self._cb_failures += 1
        if self._cb_failures >= self.CB_FAILURE_THRESHOLD:
            self._cb_opened_at = time.monotonic()

    # public request method
    async def get(self, endpoint: str, params: dict | None = None) -> object:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        params = params.copy() if params else {}

        if self.api_key:
            params["apikey"] = self.api_key

        cache_key = self._cache_key(url, params)
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        self._cb_check()

        last_exc: Exception | None = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = await self.client.get(url, params=params)

                if response.status_code == 429 or response.status_code >= 500:
                    response.raise_for_status()

                response.raise_for_status()
                payload = response.json()
                self._cb_record_success()
                self._cache_set(cache_key, payload)
                return payload

            except CircuitOpenError:
                raise

            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                self._cb_record_failure()

                if attempt == self.MAX_RETRIES:
                    break

                delay = min(
                    self.BACKOFF_BASE * (2**attempt) + random.uniform(0.0, 0.5),
                    self.BACKOFF_MAX,
                )
                await asyncio.sleep(delay)

        raise last_exc

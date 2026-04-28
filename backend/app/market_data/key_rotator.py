"""
app/market_data/key_rotator.py

Automatic API key rotation system.
When a key hits its rate limit, the next key activates seamlessly.
Plugs into: TwelveDataProvider, UpstoxProvider
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class APIKeyRotator:
    """
    Manages a pool of API keys for a single provider.

    Usage:
        rotator = APIKeyRotator(
            keys=["key1", "key2", "key3"],
            daily_limit=800,
            provider_name="TwelveData"
        )
        key = rotator.get_key()          # Always returns a valid key or None
        rotator.mark_exhausted(key)      # Force-rotate when 429 received
        stats = rotator.get_stats()      # Inspect usage
    """

    def __init__(self, keys: list[str], daily_limit: int, provider_name: str):
        self.keys = [k.strip() for k in keys if k and k.strip()]
        self.daily_limit = daily_limit
        self.provider_name = provider_name

        self._index: int = 0
        self._usage: dict[str, int] = {k: 0 for k in self.keys}
        self._exhausted: dict[str, bool] = {k: False for k in self.keys}
        self._last_reset: datetime = datetime.utcnow()

        if not self.keys:
            logger.warning(f"[KeyRotator] No API keys configured for '{provider_name}'")

    # Public interface
    def get_key(self) -> str | None:
        """
        Return the current active API key.
        Automatically rotates to the next available key when needed.
        Returns None if all keys are exhausted.
        """
        self._maybe_reset_daily_counters()

        if not self.keys:
            return None

        # Try each key starting from current index
        for _ in range(len(self.keys)):
            key = self.keys[self._index]

            if not self._exhausted[key] and self._usage[key] < self.daily_limit:
                self._usage[key] += 1
                return key

            # This key is exhausted — rotate
            self._rotate()

        logger.error(f"[KeyRotator:{self.provider_name}] All {len(self.keys)} keys exhausted.")
        return None

    def mark_exhausted(self, key: str) -> None:
        """
        Force-exhaust a key when the provider returns a 429 / rate-limit error.
        The next call to get_key() will skip this key.
        """
        if key in self._exhausted:
            self._exhausted[key] = True
            self._usage[key] = self.daily_limit
            logger.warning(f"[KeyRotator:{self.provider_name}] Key …{key[-6:]} force-exhausted. Rotating to next key.")
            self._rotate()

    def get_stats(self) -> dict:
        return {
            "provider": self.provider_name,
            "total_keys": len(self.keys),
            "active_index": self._index,
            "daily_limit_per_key": self.daily_limit,
            "last_reset_utc": self._last_reset.isoformat(),
            "keys": [
                {
                    "suffix": f"…{k[-6:]}",
                    "used": self._usage[k],
                    "remaining": max(0, self.daily_limit - self._usage[k]),
                    "exhausted": self._exhausted[k],
                }
                for k in self.keys
            ],
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _rotate(self) -> None:
        """Advance the index to the next key (wraps around)."""
        self._index = (self._index + 1) % max(len(self.keys), 1)

    def _maybe_reset_daily_counters(self) -> None:
        """Reset all counters once per calendar day (UTC)."""
        now = datetime.utcnow()
        if now - self._last_reset >= timedelta(days=1):
            self._usage = {k: 0 for k in self.keys}
            self._exhausted = {k: False for k in self.keys}
            self._index = 0
            self._last_reset = now
            logger.info(f"[KeyRotator:{self.provider_name}] Daily counters reset.")


# ------------------------------------------------------------------
# Registry — one singleton per provider, shared app-wide
# ------------------------------------------------------------------


class KeyRotatorRegistry:
    """
    Singleton registry: holds one APIKeyRotator per provider.
    Import this in providers and API routes to share state.

    Example:
        from app.market_data.key_rotator import KeyRotatorRegistry
        key = KeyRotatorRegistry.twelve_data.get_key()
    """

    twelve_data: APIKeyRotator = None  # populated by app startup
    upstox: APIKeyRotator = None  # populated by app startup

    @classmethod
    def init(
        cls,
        twelve_data_keys: list[str],
        twelve_data_limit: int,
        upstox_keys: list[str],
        upstox_limit: int,
    ) -> None:
        cls.twelve_data = APIKeyRotator(twelve_data_keys, twelve_data_limit, "TwelveData")
        cls.upstox = APIKeyRotator(upstox_keys, upstox_limit, "Upstox")
        logger.info(
            f"[KeyRotatorRegistry] Initialised — "
            f"TwelveData keys: {len(cls.twelve_data.keys)}, "
            f"Upstox keys: {len(cls.upstox.keys)}"
        )

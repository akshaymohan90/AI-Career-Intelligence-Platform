import hashlib
import json
import time
from pathlib import Path

import httpx

from app.core.config import SERPAPI_CACHE_TTL_SECONDS, SERPAPI_KEY

SERPAPI_URL = "https://serpapi.com/search.json"
CACHE_DIR = Path(__file__).resolve().parents[2] / "storage" / "serpapi_cache"


class SerpApiError(RuntimeError):
    pass


class SerpApiClient:

    def __init__(self, api_key: str | None = None, cache_dir: Path = CACHE_DIR):
        self.api_key = api_key or SERPAPI_KEY
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.live_calls = 0
        self.cache_hits = 0

    def search(self, engine: str, **params) -> dict:
        if not self.api_key:
            raise SerpApiError("SERPAPI_KEY is not configured on the server.")

        cache_key = self._cache_key(engine, params)
        cached = self._read_cache(cache_key)
        if cached is not None:
            self.cache_hits += 1
            return cached

        response = httpx.get(
            SERPAPI_URL,
            params={"engine": engine, "api_key": self.api_key, **params},
            timeout=30,
        )
        self.live_calls += 1
        if response.status_code != 200:
            raise SerpApiError(f"SerpApi {engine} request failed: HTTP {response.status_code}")

        data = response.json()
        if "error" in data:
            raise SerpApiError(f"SerpApi {engine} error: {data['error']}")

        self._write_cache(cache_key, data)
        return data

    def _cache_key(self, engine: str, params: dict) -> str:
        raw = json.dumps({"engine": engine, **params}, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _read_cache(self, key: str) -> dict | None:
        path = self.cache_dir / f"{key}.json"
        if not path.exists():
            return None
        if time.time() - path.stat().st_mtime > SERPAPI_CACHE_TTL_SECONDS:
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_cache(self, key: str, data: dict) -> None:
        (self.cache_dir / f"{key}.json").write_text(json.dumps(data), encoding="utf-8")

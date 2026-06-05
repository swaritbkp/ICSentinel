import json
import os
import time
from pathlib import Path

CACHE_DIR = Path(".ic_sentinel_cache")
CACHE_DIR.mkdir(exist_ok=True)

def _path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"

def cache_set(key: str, data, ttl: int = 1800):
    payload = {"ts": time.time(), "ttl": ttl, "data": data}
    with open(_path(key), "w") as f:
        json.dump(payload, f)

def cache_get(key: str):
    p = _path(key)
    if not p.exists():
        return None
    with open(p) as f:
        payload = json.load(f)
    if time.time() - payload["ts"] > payload["ttl"]:
        return None
    return payload["data"]

def cache_get_stale(key: str):
    """Always returns last cached value even if expired — used as fallback."""
    p = _path(key)
    if not p.exists():
        return None
    with open(p) as f:
        payload = json.load(f)
    return payload.get("data")

def cache_age_minutes(key: str) -> float:
    p = _path(key)
    if not p.exists():
        return 999.0
    with open(p) as f:
        payload = json.load(f)
    return round((time.time() - payload["ts"]) / 60, 1)

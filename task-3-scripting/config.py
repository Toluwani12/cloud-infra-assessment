"""Read health-check settings from JSON or an environment variable."""
import json
import math
import os
from pathlib import Path
from urllib.parse import urlsplit


def load_config(path):
    raw = os.environ.get("HEALTHCHECK_CONFIG")
    config = json.loads(raw if raw is not None else Path(path).read_text())
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a JSON object")
    for key, default in (("attempts", 3), ("timeout", 5), ("backoff", 1)):
        value = config.setdefault(key, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be a number")
        if not math.isfinite(value) or value < (1 if key == "attempts" else 0):
            raise ValueError(f"Invalid {key}")
    if not isinstance(config["attempts"], int) or config["timeout"] == 0:
        raise ValueError("attempts must be an integer; timeout must be positive")
    endpoints = config.get("endpoints")
    if not isinstance(endpoints, list) or not endpoints:
        raise ValueError("endpoints must be a nonempty list")
    for endpoint in endpoints:
        if not isinstance(endpoint, dict) or not isinstance(endpoint.get("url"), str):
            raise ValueError("Each endpoint needs a URL")
        url = urlsplit(endpoint["url"])
        if url.scheme not in ("http", "https") or not url.hostname or url.username:
            raise ValueError("Use HTTP(S) URLs without embedded credentials")
        status = endpoint.setdefault("expected_status", 200)
        if type(status) is not int or not 100 <= status <= 599:
            raise ValueError("expected_status must be an HTTP status integer")
    return config

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ENV_FILE = ROOT / ".env.runtime.local"


def load_runtime_env(env_file: Path | None = None) -> dict[str, str]:
    values = dict(os.environ)
    path = env_file or DEFAULT_ENV_FILE
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in values:
            values[key] = value
    return values

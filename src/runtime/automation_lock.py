from __future__ import annotations

import argparse
import json
import os
import socket
from pathlib import Path
from time import time


DEFAULT_LOCK_ROOT = Path("/tmp/grounded-deck-automation-locks")
DEFAULT_STALE_SECONDS = 60 * 60


class AutomationLockHeldError(RuntimeError):
    def __init__(self, role: str, info: dict) -> None:
        self.role = role
        self.info = info
        super().__init__(f"automation lock already held for role {role}")


def resolve_lock_root(lock_root: Path | None = None) -> Path:
    if lock_root is not None:
        return lock_root
    env_value = os.environ.get("GROUNDED_DECK_AUTOMATION_LOCK_ROOT")
    return Path(env_value) if env_value else DEFAULT_LOCK_ROOT


def lock_path(role: str, lock_root: Path | None = None) -> Path:
    return resolve_lock_root(lock_root) / f"{role}.json"


def _read_lock(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _is_stale(info: dict | None, stale_seconds: int, now: float | None = None) -> bool:
    if not info:
        return True
    created_at = info.get("created_at_unix")
    if not isinstance(created_at, (int, float)):
        return True
    current_time = time() if now is None else now
    return current_time - float(created_at) > stale_seconds


def acquire_lock(
    *,
    role: str,
    owner: str,
    repo_root: str,
    lock_root: Path | None = None,
    stale_seconds: int = DEFAULT_STALE_SECONDS,
    now: float | None = None,
) -> dict:
    root = resolve_lock_root(lock_root)
    root.mkdir(parents=True, exist_ok=True)
    path = lock_path(role, root)
    created_at = int(time() if now is None else now)
    payload = {
        "role": role,
        "owner": owner,
        "repo_root": repo_root,
        "created_at_unix": created_at,
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
    }

    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            existing = _read_lock(path)
            if _is_stale(existing, stale_seconds=stale_seconds, now=now):
                path.unlink(missing_ok=True)
                continue
            raise AutomationLockHeldError(role, existing)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        return payload


def release_lock(*, role: str, lock_root: Path | None = None) -> bool:
    path = lock_path(role, lock_root)
    if not path.exists():
        return False
    path.unlink()
    return True


def get_lock_status(
    *,
    role: str,
    lock_root: Path | None = None,
    stale_seconds: int = DEFAULT_STALE_SECONDS,
    now: float | None = None,
) -> dict:
    path = lock_path(role, lock_root)
    info = _read_lock(path)
    return {
        "role": role,
        "lock_path": str(path),
        "held": path.exists() and info is not None and not _is_stale(info, stale_seconds, now),
        "stale": path.exists() and _is_stale(info, stale_seconds, now),
        "info": info,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage GroundedDeck automation role locks.")
    parser.add_argument("action", choices=("acquire", "release", "status"))
    parser.add_argument("role", choices=("worker", "curator"))
    parser.add_argument("--owner", default="unknown")
    parser.add_argument("--repo-root", default=str(Path.cwd()))
    parser.add_argument("--stale-seconds", type=int, default=DEFAULT_STALE_SECONDS)
    args = parser.parse_args()

    if args.action == "acquire":
        try:
            payload = acquire_lock(
                role=args.role,
                owner=args.owner,
                repo_root=args.repo_root,
                stale_seconds=args.stale_seconds,
            )
        except AutomationLockHeldError as exc:
            info = exc.info or {}
            print(
                json.dumps(
                    {
                        "result": "held",
                        "role": args.role,
                        "owner": info.get("owner"),
                        "repo_root": info.get("repo_root"),
                        "created_at_unix": info.get("created_at_unix"),
                    },
                    ensure_ascii=False,
                )
            )
            return 2

        print(json.dumps({"result": "acquired", **payload}, ensure_ascii=False))
        return 0

    if args.action == "release":
        released = release_lock(role=args.role)
        print(json.dumps({"result": "released" if released else "not-held", "role": args.role}, ensure_ascii=False))
        return 0

    print(json.dumps(get_lock_status(role=args.role, stale_seconds=args.stale_seconds), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

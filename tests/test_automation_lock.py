from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.runtime.automation_lock import (
    AutomationLockHeldError,
    acquire_lock,
    get_lock_status,
    release_lock,
)


class AutomationLockTests(unittest.TestCase):
    def test_acquire_and_release_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_root = Path(tmpdir)
            payload = acquire_lock(
                role="worker",
                owner="worker-a",
                repo_root="/tmp/repo",
                lock_root=lock_root,
                now=100,
            )

            self.assertEqual(payload["owner"], "worker-a")
            self.assertTrue((lock_root / "worker.json").exists())
            self.assertTrue(release_lock(role="worker", lock_root=lock_root))
            self.assertFalse((lock_root / "worker.json").exists())

    def test_acquire_fails_while_fresh_lock_is_held(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_root = Path(tmpdir)
            acquire_lock(
                role="curator",
                owner="curator-a",
                repo_root="/tmp/repo",
                lock_root=lock_root,
                now=100,
            )

            with self.assertRaises(AutomationLockHeldError):
                acquire_lock(
                    role="curator",
                    owner="curator-b",
                    repo_root="/tmp/repo",
                    lock_root=lock_root,
                    now=120,
                    stale_seconds=60,
                )

    def test_stale_lock_is_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_root = Path(tmpdir)
            acquire_lock(
                role="worker",
                owner="worker-a",
                repo_root="/tmp/repo",
                lock_root=lock_root,
                now=100,
            )

            payload = acquire_lock(
                role="worker",
                owner="worker-b",
                repo_root="/tmp/repo",
                lock_root=lock_root,
                now=5000,
                stale_seconds=60,
            )

            self.assertEqual(payload["owner"], "worker-b")

    def test_status_reports_held_and_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_root = Path(tmpdir)
            acquire_lock(
                role="curator",
                owner="curator-a",
                repo_root="/tmp/repo",
                lock_root=lock_root,
                now=100,
            )

            held = get_lock_status(role="curator", lock_root=lock_root, now=120, stale_seconds=60)
            stale = get_lock_status(role="curator", lock_root=lock_root, now=1000, stale_seconds=60)

            self.assertTrue(held["held"])
            self.assertFalse(held["stale"])
            self.assertFalse(stale["held"])
            self.assertTrue(stale["stale"])


if __name__ == "__main__":
    unittest.main()

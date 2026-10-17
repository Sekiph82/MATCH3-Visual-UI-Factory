"""R44 player-pack quarantine: no exports or owner authority created."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from factory.export_pipeline.player_pack_preflight import (
    PlayerPackError, audit_candidate
)


class PlayerPackPreflightTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name) / "player_pack"
        self.root.mkdir()

    def sample(self, name="visuals/tile.png", contents=b"PNG_TEST_PLACEHOLDER"):
        path = self.root / name
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_bytes(contents)
        return path

    def test_regular_content_receipts_stay_review_only(self):
        self.sample()
        report = audit_candidate(self.root)
        self.assertTrue(report["content_clean"])
        self.assertFalse(report["release_allowed"])
        self.assertEqual(report["file_count"], 1)
        self.assertEqual(report["files"][0]["sha256"],
                         hashlib.sha256(b"PNG_TEST_PLACEHOLDER").hexdigest())
        self.assertEqual(report["original_art_rights_gate"], "NOT_VERIFIED")

    def test_reject_editor_code_tests_and_dev_evidence(self):
        for name in ("Editor/Tool.cs", "tests/test_marker.py",
                     "docs/notes.md", ".git/config", "logs/output.txt"):
            with self.subTest(name=name):
                self.sample(name)
                report = audit_candidate(self.root)
                self.assertFalse(report["content_clean"])
                self.assertFalse(report["release_allowed"])
                self.assertTrue(any(x["reason"] == "PROHIBITED_DIRECTORY"
                                    for x in report["findings"]))
                (self.root / name).unlink()

    def test_unknown_dangerous_extensions_never_look_like_runtime_assets(self):
        for name in ("code.dll", "company.pdb", "fancy.ttf",
                     "passwords.env", "snapshot.webp", "level.cs"):
            with self.subTest(name=name):
                self.sample(name)
                report = audit_candidate(self.root)
                self.assertFalse(report["content_clean"])
                self.assertTrue(any("FORBIDDEN_RELEASE_CONTENT" == x["reason"]
                                    for x in report["findings"]))
                (self.root / name).unlink()

    def test_serialized_test_candidate_and_editor_markers_are_rejected(self):
        for text in (b"status: TEST_ONLY", b"CANDIDATE_NOT_OWNER_APPROVED",
                     b"asset: AUTHORING_ONLY", b"UnityEditor.MenuItem"):
            with self.subTest(text=text):
                path = self.sample("data/state.prefab", text)
                report = audit_candidate(self.root)
                self.assertTrue(any(x["reason"] == "NON_SHIPPING_MARKER"
                                    for x in report["findings"]))
                path.unlink()

    def test_credentials_in_json_are_not_accepted(self):
        path = self.sample("data/manifest.json", b'{"api_key":"example-secret-123"}')
        report = audit_candidate(self.root)
        self.assertTrue(any(x["reason"] == "POTENTIAL_SECRET"
                            for x in report["findings"]))
        self.assertFalse(report["release_allowed"])
        self.assertEqual(path.read_bytes(), b'{"api_key":"example-secret-123"}')

    def test_reserved_package_metadata_rejected(self):
        for name in ("TASKS.md", "packages-lock.json", "credentials.json"):
            with self.subTest(name=name):
                self.sample(name)
                self.assertTrue(any(x["reason"] == "FORBIDDEN_RELEASE_CONTENT"
                                    for x in audit_candidate(self.root)["findings"]))
                (self.root / name).unlink()

    def test_unreadable_or_absent_candidate_root_fails_closed(self):
        with self.assertRaises(PlayerPackError):
            audit_candidate(self.root / "missing")
        with self.assertRaises(PlayerPackError):
            audit_candidate(self.root / "missing" / "more")

    def test_oversize_or_empty_file_is_reported_without_reading(self):
        self.sample(contents=b"")
        report = audit_candidate(self.root)
        self.assertFalse(report["content_clean"])
        self.assertEqual(report["findings"][0]["reason"], "OVERSIZE_OR_EMPTY_FILE")
        self.assertEqual(report["total_scanned_bytes"], 0)

    def test_too_many_files_fail_closed(self):
        for index in range(513):
            self.sample("parts/tile_%03d.png" % index, b"test")
        with self.assertRaises(PlayerPackError):
            audit_candidate(self.root)

    def test_case_insensitive_filename_collision_rejected(self):
        self.sample("tiles/A.png", b"file a")
        other = self.root / "tiles/a.png"
        other.write_bytes(b"file b")
        # Filesystems with case-insensitive matching cannot contain both.
        if (self.root / "tiles/A.png").read_bytes() == b"file a":
            report = audit_candidate(self.root)
            self.assertTrue(any(x["reason"] == "CASE_INSENSITIVE_COLLISION"
                                for x in report["findings"]))

    def test_symlink_source_never_followed_when_supported(self):
        src = self.sample("good.png")
        link = self.root / "bad.png"
        try:
            link.symlink_to(src)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is disabled on this Windows environment")
        with self.assertRaises(PlayerPackError):
            audit_candidate(self.root)
        self.assertEqual(src.read_bytes(), b"PNG_TEST_PLACEHOLDER")

    def test_read_only_scanner_does_not_modify_files(self):
        original = self.sample("visuals/a.prefab", b"normal-content")
        before = original.stat().st_mtime_ns
        first = audit_candidate(self.root)
        second = audit_candidate(self.root)
        self.assertEqual(first, second)
        self.assertEqual(original.stat().st_mtime_ns, before)


if __name__ == "__main__":
    unittest.main()

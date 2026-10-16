"""R19 offline translation coverage and copy-integrity tests."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from factory.ui_composer.locale_audit import (
    LocaleAuditError, audit_file, save_once, main, ROOT,
)


class LocaleDraftTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.work = Path(temp.name)
        self.source = self.work / "tr-draft.json"
        self.document = {
            "schema_version": 1,
            "stage": "LOCALIZATION_DRAFT_NOT_APPROVED",
            "profile_id": "Coral_Rescue",
            "locales": {
                "en": {"home": "Home", "gameplay_hud": "Gameplay"},
                "tr": {"home": "Ana Sayfa", "gameplay_hud": "Oyun Ekranı"}
            }
        }
        self.write()

    def write(self):
        self.source.write_text(json.dumps(self.document, ensure_ascii=False),
                               encoding="utf-8")

    def test_draft_report_never_claims_approval_or_game_binding(self):
        report = audit_file(self.source)
        self.assertEqual(report["stage"], "REVIEW_REQUIRED_NOT_APPROVED")
        self.assertFalse(report["owner_translation_approved"])
        self.assertFalse(report["game_bindings_enabled"])
        self.assertEqual(len(report["locales"]), 2)
        self.assertEqual(report["locales"][0]["covered"], 2)
        self.assertEqual(report["locales"][1]["total"], 28)
        self.assertEqual(report["locales"][1]["coverage_basis_points"], 714)

    def test_turkish_diacritics_are_kept_as_unicode(self):
        self.document["locales"]["tr"]["world_map"] = "Dünya Haritası"
        self.write()
        self.assertEqual(audit_file(self.source)["locales"][1]["covered"], 3)

    def test_screens_with_policy_off_are_recorded_not_enabled(self):
        report = audit_file(self.source)
        self.assertEqual(len(report["policy_off_keys"]), 5)
        self.assertIn("friends", report["policy_off_keys"])
        self.assertFalse(report["game_bindings_enabled"])

    def test_overlong_draft_copy_requires_review_not_approval(self):
        self.document["locales"]["tr"]["home"] = "Bu bir uzun ve kasıtlı taslak başlıktır"
        self.write()
        report = audit_file(self.source)
        self.assertIn("home", report["locales"][1]["long_copy_review_keys"])
        self.assertIn("EXPANDED_COPY_REVIEW: tr", report["warning_codes"])

    def test_overbudget_source_rejected(self):
        self.document["locales"]["tr"]["home"] = "A" * 241
        self.write()
        with self.assertRaises(LocaleAuditError):
            audit_file(self.source)

    def test_unknown_screen_key_rejected(self):
        self.document["locales"]["en"]["does_not_exist"] = "Bad"
        self.write()
        with self.assertRaises(LocaleAuditError):
            audit_file(self.source)

    def test_unknown_profile_or_forged_stage_rejected(self):
        for field, value in (("profile_id", "Garage_Legends"),
                             ("stage", "OWNER_APPROVED"),
                             ("schema_version", True)):
            with self.subTest(field=field):
                original = self.document[field]
                self.document[field] = value
                self.write()
                with self.assertRaises(LocaleAuditError):
                    audit_file(self.source)
                self.document[field] = original

    def test_duplicate_json_key_rejected(self):
        self.source.write_text(
            '{"schema_version":1,"schema_version":1,"stage":"LOCALIZATION_DRAFT_NOT_APPROVED"}',
            encoding="utf-8")
        with self.assertRaises(LocaleAuditError):
            audit_file(self.source)

    def test_rtl_override_and_control_characters_rejected(self):
        for text in ("Home\u202e", "Bad\nLine", "Hidden\u200b"):
            self.document["locales"]["en"]["home"] = text
            self.write()
            with self.assertRaises(LocaleAuditError):
                audit_file(self.source)

    def test_en_tr_placeholder_parity(self):
        self.document["locales"]["en"]["home"] = "Welcome {player_name}"
        self.document["locales"]["tr"]["home"] = "Hoş geldin {player_name}"
        self.write()
        self.assertIn("home", audit_file(self.source)["shared_placeholder_checked_keys"])
        self.document["locales"]["tr"]["home"] = "Merhaba {other}"
        self.write()
        with self.assertRaises(LocaleAuditError):
            audit_file(self.source)

    def test_missing_or_malformed_placeholder_rejected(self):
        self.document["locales"]["en"]["home"] = "Welcome {player"
        self.write()
        with self.assertRaises(LocaleAuditError):
            audit_file(self.source)

    def test_empty_locales_rejected(self):
        self.document["locales"] = {"en": {}, "tr": {}}
        self.write()
        with self.assertRaises(LocaleAuditError):
            audit_file(self.source)

    def test_extra_locale_rejected(self):
        self.document["locales"]["de"] = {"home": "Start"}
        self.write()
        with self.assertRaises(LocaleAuditError):
            audit_file(self.source)

    def test_write_once_external_output_protects_previous_report(self):
        report = audit_file(self.source)
        destination = self.work / "coverage.json"
        save_once(report, destination)
        previous = destination.read_bytes()
        with self.assertRaises(LocaleAuditError):
            save_once(report, destination)
        self.assertEqual(destination.read_bytes(), previous)

    def test_output_inside_git_repo_rejected(self):
        with self.assertRaises(LocaleAuditError):
            save_once(audit_file(self.source), ROOT / "forbidden-locale-report.json")

    def test_fake_link_source_rejected_without_windows_privileges(self):
        from factory.ui_composer import locale_audit
        actual = locale_audit._is_link
        with patch.object(locale_audit, "_is_link",
                          side_effect=lambda p: Path(p) == self.source or actual(p)):
            with self.assertRaises(LocaleAuditError):
                audit_file(self.source)

    def test_cli_stdout_does_not_create_artifacts(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--draft", str(self.source)]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["locales"][0]["covered"], 2)
        self.assertEqual(list(self.work.glob("*.json")), [self.source])

    def test_cli_invalid_stage_returns_error(self):
        self.document["stage"] = "PRODUCTION_APPROVED"
        self.write()
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--draft", str(self.source)]), 2)


if __name__ == "__main__":
    unittest.main()

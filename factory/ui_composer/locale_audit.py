"""VF-07 / VF-08: read-only draft EN/TR coverage and copy-risk audit.

Source is a user-supplied OFFLINE draft JSON outside Git. The tool never
writes translations into a game, grants approvals, or certifies linguistic
quality. The exact 28 Coral contract keys remain immutable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "schemas/coral-experiences.v1.json"
STAGE = "LOCALIZATION_DRAFT_NOT_APPROVED"
REPORT_STAGE = "REVIEW_REQUIRED_NOT_APPROVED"
LANGUAGES = ("en", "tr")
MAX_INPUT_BYTES = 256 * 1024
MAX_TEXT_LENGTH = 240
MAX_PREVIEW_LENGTH = 36
PLACEHOLDER = re.compile(r"\{[A-Za-z][A-Za-z0-9_]*\}")
ALLOWED_KEYS = frozenset(("schema_version", "stage", "profile_id", "locales"))


class LocaleAuditError(ValueError):
    pass


def _unique_object(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise LocaleAuditError("duplicate JSON key: " + key)
        data[key] = value
    return data


def _is_link(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    metadata = path.stat(follow_symlinks=False)
    return bool(getattr(metadata, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _external_read(path: Path) -> bytes:
    path = Path(path)
    if not path.is_file() or _is_link(path):
        raise LocaleAuditError("expected existing real draft JSON file")
    if any(_is_link(part) for part in path.parents):
        raise LocaleAuditError("draft JSON cannot be reached through linked folders")
    if path.resolve(strict=True).is_relative_to(ROOT):
        raise LocaleAuditError("draft translations must be external to source repository")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise LocaleAuditError("draft JSON exceeds 256KiB limit")
    return path.read_bytes()


def _decode(raw: bytes) -> dict:
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeError, ValueError) as exc:
        raise LocaleAuditError("invalid UTF-8 or duplicate/malformed JSON: " + str(exc)) from exc
    if not isinstance(doc, dict) or set(doc) != ALLOWED_KEYS:
        raise LocaleAuditError("unknown draft manifest fields")
    if type(doc["schema_version"]) is not int or doc["schema_version"] != 1:
        raise LocaleAuditError("unsupported localization draft version")
    if doc["stage"] != STAGE or doc["profile_id"] != "Coral_Rescue":
        raise LocaleAuditError("owner-approved state or unknown profile forbidden")
    if not isinstance(doc["locales"], dict) or set(doc["locales"]) != set(LANGUAGES):
        raise LocaleAuditError("exactly English and Turkish draft maps required")
    return doc


def _validate_text(value: object, key: str) -> set[str]:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT_LENGTH:
        raise LocaleAuditError("empty, non-text or over-budget translation for " + key)
    if any(unicodedata.category(c) in ("Cc", "Cf", "Cs") for c in value):
        raise LocaleAuditError("invisible/control/BiDi codepoint in " + key)
    if value != value.strip():
        raise LocaleAuditError("leading or trailing whitespace in " + key)
    matches = PLACEHOLDER.findall(value)
    unbraced = PLACEHOLDER.sub("", value)
    if "{" in unbraced or "}" in unbraced:
        raise LocaleAuditError("malformed placeholder in " + key)
    return set(matches)


def audit_file(path: Path) -> dict:
    original = _external_read(Path(path))
    doc = _decode(original)
    contract_bytes = CONTRACT.read_bytes()
    contract = json.loads(contract_bytes.decode("utf-8"))
    if (contract.get("schema_version") != 1 or
            contract.get("profile_id") != "Coral_Rescue" or
            contract.get("status") != "CONTRACT_DRAFT_NOT_IMPLEMENTED" or
            len(contract.get("screens", [])) != 28):
        raise LocaleAuditError("canonical 28-screen contract changed")
    keys = [item["key"] for item in contract["screens"]]
    if len(keys) != len(set(keys)):
        raise LocaleAuditError("duplicate canonical screen keys")
    allowed = set(keys)
    protected = {item["key"] for item in contract["screens"] if
                 item["feature_gate"] == "OFF_UNTIL_ENGINE_POLICY_CONFIRMED"}
    for locale in LANGUAGES:
        entries = doc["locales"][locale]
        if not isinstance(entries, dict) or not set(entries).issubset(allowed):
            raise LocaleAuditError("unknown screen key for locale " + locale)
        for key, value in entries.items():
            _validate_text(value, locale + "." + key)
    if not any(doc["locales"][language] for language in LANGUAGES):
        raise LocaleAuditError("draft must have at least one translated screen heading")

    statuses = []
    warnings = []
    for locale in LANGUAGES:
        translations = doc["locales"][locale]
        missing = [key for key in keys if key not in translations]
        long = [key for key in keys if key in translations and
                len(translations[key]) > MAX_PREVIEW_LENGTH]
        statuses.append({
            "locale": locale, "covered": len(translations),
            "total": len(keys), "coverage_basis_points":
                len(translations) * 10000 // len(keys),
            "missing_keys": missing, "long_copy_review_keys": long
        })
        if missing:
            warnings.append("INCOMPLETE_LOCALE: " + locale)
        if long:
            warnings.append("EXPANDED_COPY_REVIEW: " + locale)
    placeholders = []
    both = set(doc["locales"]["en"]).intersection(doc["locales"]["tr"])
    for key in sorted(both):
        english = _validate_text(doc["locales"]["en"][key], "en." + key)
        turkish = _validate_text(doc["locales"]["tr"][key], "tr." + key)
        if english != turkish:
            raise LocaleAuditError("EN/TR placeholder mismatch: " + key)
        if english:
            placeholders.append(key)

    return {
        "schema_version": 1,
        "stage": REPORT_STAGE,
        "profile_id": "Coral_Rescue",
        "source_manifest_sha256": hashlib.sha256(original).hexdigest(),
        "source_contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "locales": statuses,
        "shared_placeholder_checked_keys": placeholders,
        "policy_off_keys": sorted(protected),
        "warning_codes": warnings,
        "owner_translation_approved": False,
        "game_bindings_enabled": False,
        "report_type": "OFFLINE_DRAFT_COVERAGE_V01"
    }


def save_once(report: dict, destination: Path) -> None:
    path = Path(destination)
    if path.exists() or path.is_symlink() or path.resolve().is_relative_to(ROOT):
        raise LocaleAuditError("external output must be new; no overwrites")
    if not path.parent.is_dir() or any(_is_link(parent) for parent in
                                       (path.parent, *path.parent.parents)):
        raise LocaleAuditError("report output directory must be an existing real folder")
    with path.open("x", encoding="utf-8", newline="\n") as target:
        json.dump(report, target, ensure_ascii=False, indent=2, sort_keys=True)
        target.write("\n")
        target.flush()
        os.fsync(target.fileno())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--output-file", type=Path)
    args = parser.parse_args(argv)
    try:
        report = audit_file(args.draft)
        if args.output_file:
            save_once(report, args.output_file)
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    except (LocaleAuditError, OSError, UnicodeError, ValueError) as exc:
        print("VUF_LOCALE_DRAFT_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

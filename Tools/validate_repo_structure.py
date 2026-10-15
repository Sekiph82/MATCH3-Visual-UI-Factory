"""Lightweight source-layout checks, NOT a substitute for Unity Editor tests."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "unity_package"


def validate_structure() -> dict:
    project = json.loads((ROOT / "Packages/manifest.json").read_text(encoding="utf-8"))
    package = json.loads((PACKAGE / "package.json").read_text(encoding="utf-8"))
    runtime = json.loads((PACKAGE / "Runtime/Match3.VisualFactory.Runtime.asmdef").read_text())
    editor = json.loads((PACKAGE / "Editor/Match3.VisualFactory.Editor.asmdef").read_text())
    if project["dependencies"].get("com.match3.visual-factory") != "file:../unity_package":
        raise ValueError("project does not import actual local UPM package")
    if package.get("name") != "com.match3.visual-factory":
        raise ValueError("package identity mismatch")
    if runtime.get("name") != "Match3.VisualFactory.Runtime" or runtime.get("includePlatforms"):
        raise ValueError("runtime assembly unexpectedly tied to Editor")
    if editor.get("includePlatforms") != ["Editor"]:
        raise ValueError("Editor assembly may enter a player build")
    if editor.get("references") != ["Match3.VisualFactory.Runtime"]:
        raise ValueError("Editor consumer must reference runtime read-only contracts")
    wanted = [
        "Runtime.meta", "Editor.meta",
        "Runtime/Match3.VisualFactory.Runtime.asmdef",
        "Editor/Match3.VisualFactory.Editor.asmdef",
        "Runtime/VisualAssetManifest.cs",
        "Editor/VufDashboardWindow.cs",
        "Editor/VufStudioWindow.cs",
        "Editor/VufSpriteClipBuilderWindow.cs",
    ]
    guids = []
    for name in wanted:
        path = PACKAGE / name
        if not path.is_file():
            raise ValueError("missing Unity package source " + name)
        meta = path if path.suffix == ".meta" else Path(str(path) + ".meta")
        if not meta.is_file():
            raise ValueError("missing stable GUID .meta for " + name)
        ids = re.findall(r"(?m)^guid: ([0-9a-f]{32})$", meta.read_text())
        if len(ids) != 1:
            raise ValueError("invalid or missing .meta GUID " + name)
        guids.extend(ids)
    if len(guids) != len(set(guids)):
        raise ValueError("duplicate Unity meta GUID")
    if (ROOT / "Assets/Editor/VufStudioWindow.cs").exists():
        raise ValueError("stale duplicate Editor script in host project")
    if not (ROOT / "scripts/prepare_visual_factory.ps1").is_file():
        raise ValueError("safe owner-local setup script missing")
    return {"package": package["name"], "unique_guids": len(guids)}


if __name__ == "__main__":
    print(validate_structure())

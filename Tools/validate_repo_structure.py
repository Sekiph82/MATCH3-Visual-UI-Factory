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
    if project.get("testables") != ["com.match3.visual-factory"]:
        raise ValueError("package EditMode tests must be discoverable in Unity Test Runner")
    if package.get("name") != "com.match3.visual-factory":
        raise ValueError("package identity mismatch")
    if runtime.get("name") != "Match3.VisualFactory.Runtime" or runtime.get("includePlatforms"):
        raise ValueError("runtime assembly unexpectedly tied to Editor")
    if editor.get("includePlatforms") != ["Editor"]:
        raise ValueError("Editor assembly may enter a player build")
    if editor.get("references") != ["Match3.VisualFactory.Runtime", "UnityEngine.UI"]:
        raise ValueError("Editor must reference runtime and uGUI assemblies explicitly")
    if package.get("dependencies", {}).get("com.unity.ugui") != "2.6.0":
        raise ValueError("Unity 6000.6 uGUI core version is missing")
    wanted = [
        "Runtime.meta", "Editor.meta", "Editor/Resources.meta",
        "Runtime/Match3.VisualFactory.Runtime.asmdef",
        "Editor/Match3.VisualFactory.Editor.asmdef",
        "Runtime/VisualAssetManifest.cs",
        "Editor/VufDashboardWindow.cs",
        "Editor/VufStudioWindow.cs",
        "Editor/VufSpriteClipBuilderWindow.cs",
        "Editor/VufVfxLabWindow.cs",
        "Editor/VufFxSheetPreviewWindow.cs",
        "Editor/VufFxClipExporterWindow.cs",
        "Tests/Editor/VufFxClipExporterEditModeTests.cs",
        "Tests/Editor/VufFxSheetEditModeTests.cs",
        "Editor/VufUiComposerWindow.cs",
        "Editor/VufQaStudioWindow.cs",
        "Editor/VufAtlasPreviewWindow.cs",
        "Editor/VufScreenShellBuilderWindow.cs",
        "Editor/VufReviewStateCatalog.cs",
        "Editor/VufProductionQueueWindow.cs",
        "Editor/VufResponsiveGeometry.cs",
        "Editor/VufTypographyAudit.cs",
        "Editor/VufTypographyLabWindow.cs",
        "Editor/VufLocaleCoverageWindow.cs",
        "Editor/VufReadinessBoardWindow.cs",
        "Tests/Editor/VufReadinessBoardEditModeTests.cs",
        "Tests/Editor/VufLocaleCoverageEditModeTests.cs",
        "Tests/Editor/VufTypographyEditModeTests.cs",
        "Editor/VufResponsivePreviewWindow.cs",
        "Editor/VufSpriteQaReportWindow.cs",
        "Editor/VufScreenCatalog.cs",
        "Runtime/VufCandidateScreenMarker.cs",
        "Editor/Resources/coral-experiences.v1.json",
        "Editor/Resources/style_profiles.v1.json",
        "Editor/AssemblyInfo.cs",
        "Tests.meta", "Tests/Editor.meta",
        "Tests/Editor/Match3.VisualFactory.Editor.Tests.asmdef",
        "Tests/Editor/VufCatalogEditModeTests.cs",
        "Tests/Editor/VufSpriteQaEditModeTests.cs",
        "Tests/Editor/VufReviewStateEditModeTests.cs",
        "Runtime/VufSafeAreaFitter.cs",
        "Runtime/VufUiTween.cs",
        "Editor/VufUiTweenInspector.cs",
    ]
    tests = json.loads((PACKAGE / "Tests/Editor/Match3.VisualFactory.Editor.Tests.asmdef").read_text())
    if (tests.get("includePlatforms") != ["Editor"]
            or tests.get("defineConstraints") != ["UNITY_INCLUDE_TESTS"]
            or "TestAssemblies" not in tests.get("optionalUnityReferences", [])
            or tests.get("name") != "Match3.VisualFactory.Editor.Tests"):
        raise ValueError("EditMode test assembly must be isolated from normal builds")
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
    required_project_metas = [
        ROOT / "Assets/README.md.meta",
        PACKAGE / "package.json.meta",
    ]
    for meta in required_project_metas:
        if not meta.is_file():
            raise ValueError("missing stable project/package GUID .meta " + str(meta.relative_to(ROOT)))
        ids = re.findall(r"(?m)^guid: ([0-9a-f]{32})$", meta.read_text())
        if len(ids) != 1:
            raise ValueError("invalid or missing .meta GUID " + str(meta.relative_to(ROOT)))
        guids.extend(ids)
    if len(guids) != len(set(guids)):
        raise ValueError("duplicate Unity meta GUID")
    mirrors = [
        (ROOT / "schemas/coral-experiences.v1.json",
         PACKAGE / "Editor/Resources/coral-experiences.v1.json"),
        (ROOT / "factory/visual_director/style_profiles.v1.json",
         PACKAGE / "Editor/Resources/style_profiles.v1.json")
    ]
    for canonical, packaged in mirrors:
        if canonical.read_bytes() != packaged.read_bytes():
            raise ValueError("Unity catalog mirror stale: " + packaged.name)
    coral = json.loads(mirrors[0][0].read_text(encoding="utf-8"))
    if len(coral["screens"]) != 28 or len({
            item["key"] for item in coral["screens"]}) != 28:
        raise ValueError("Coral draft coverage is not 28 unique experiences")
    if [x["id"] for x in coral["screens"]] != [
            "COR-%02d" % n for n in range(1, 29)]:
        raise ValueError("Coral stable identifiers have drifted")
    if (ROOT / "Assets/Editor/VufStudioWindow.cs").exists():
        raise ValueError("stale duplicate Editor script in host project")
    if not (ROOT / "scripts/prepare_visual_factory.ps1").is_file():
        raise ValueError("safe owner-local setup script missing")
    return {"package": package["name"], "unique_guids": len(guids)}


if __name__ == "__main__":
    print(validate_structure())

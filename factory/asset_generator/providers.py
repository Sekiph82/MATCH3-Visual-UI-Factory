"""VF-03 provider-neutral intake: offline manual first, paid providers disabled.

There are intentionally NO network clients, tokens or billable calls here.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys

# Offline CLI works when invoked by path from any current working directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from factory.asset_catalog.catalog import (
    AssetCatalog, CatalogError, PROFILES, MAX_FILE_BYTES, png_dimensions
)


@dataclass(frozen=True)
class VisualRequest:
    profile_id: str
    asset_key: str
    style_version: str
    width: int
    height: int
    prompt_reference: str
    allowed_cost_usd: float = 0.0

    def validate(self):
        if self.profile_id not in PROFILES:
            raise CatalogError("unknown game profile")
        if not re.fullmatch(r"[a-z][a-z0-9_.-]{0,99}", self.asset_key):
            raise CatalogError("unsafe asset key")
        if not re.fullmatch(r"\d+\.\d+\.\d+", self.style_version):
            raise CatalogError("invalid style version")
        if self.width <= 0 or self.height <= 0 or self.width > 8192 or self.height > 8192:
            raise CatalogError("invalid image dimensions")
        if not isinstance(self.prompt_reference, str) or not self.prompt_reference.strip():
            raise CatalogError("prompt/version or owner-reference identifier required")
        if self.allowed_cost_usd != 0.0:
            raise CatalogError("paid generation not authorized by this offline baseline")


class ManualFileProvider:
    provider_id = "manual_file"
    supports_ai_generation = False
    requires_credentials = False
    billable = False

    def import_png(self, request: VisualRequest, catalog: AssetCatalog, image: Path,
                   rights: str, source_receipt: str) -> dict:
        request.validate()
        path = Path(image)
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
            raise CatalogError("manual intake requires regular bounded PNG source")
        data = path.read_bytes()
        if len(data) > MAX_FILE_BYTES:
            raise CatalogError("source exceeds bounded intake")
        width, height = png_dimensions(data)
        if (width, height) != (request.width, request.height):
            raise CatalogError("provided source dimensions differ from request")
        receipt = source_receipt + " | visual-request:" + request.prompt_reference
        return catalog.ingest(image, request.profile_id, request.asset_key, rights, receipt)


class ProviderRegistry:
    def __init__(self):
        self._providers = {"manual_file": ManualFileProvider()}

    def available(self):
        return [
            {"id": "manual_file", "status": "OFFLINE_INTAKE", "billable": False},
            {"id": "external_ai", "status": "NOT_INSTALLED_OR_AUTHORIZED", "billable": True},
        ]

    def get(self, provider_id: str):
        if provider_id not in self._providers:
            raise CatalogError("provider disabled or unknown: " + str(provider_id))
        return self._providers[provider_id]

    def generate(self, provider_id: str, request: VisualRequest):
        request.validate()
        raise CatalogError("automatic provider generation disabled; import source PNG manually")


def main():
    import json
    print(json.dumps(ProviderRegistry().available(), indent=2))


if __name__ == "__main__":
    main()

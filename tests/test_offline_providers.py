import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from factory.asset_catalog.catalog import AssetCatalog, CatalogError
from factory.asset_generator.providers import VisualRequest, ProviderRegistry


def chunk(name, data):
    return (struct.pack(">I", len(data)) + name + data +
            struct.pack(">I", zlib.crc32(name + data) & 0xffffffff))


def png():
    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) +
            chunk(b"IDAT", zlib.compress(b"\x00\x23\x66\xff\xff")) +
            chunk(b"IEND", b""))


def request(**kwargs):
    return VisualRequest("Coral_Rescue", "tile.shield", "0.1.0",
                         1, 1, "brief-R04", **kwargs)


class OfflineProvidersTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store = AssetCatalog(self.root / "asset-store")
        self.store.init()
        self.original = self.root / "original.png"
        self.original.write_bytes(png())
        self.registry = ProviderRegistry()

    def test_manual_provider_ingests_candidate_not_approved(self):
        result = self.registry.get("manual_file").import_png(
            request(), self.store, self.original, "original", "owner-media")
        self.assertEqual(result["stage"], "CANDIDATE")
        self.assertEqual(self.store.verify()["active_assets"], 0)

    def test_uninstalled_ai_provider_refuses(self):
        with self.assertRaises(CatalogError):
            self.registry.get("external_ai")
        with self.assertRaises(CatalogError):
            self.registry.generate("external_ai", request())

    def test_paid_request_blocked_by_default(self):
        with self.assertRaises(CatalogError):
            request(allowed_cost_usd=1).validate()

    def test_manual_wrong_dimensions_rejected(self):
        bad = VisualRequest("Coral_Rescue", "tile.shield", "0.1.0",
                            2, 1, "brief-R04")
        with self.assertRaises(CatalogError):
            self.registry.get("manual_file").import_png(
                bad, self.store, self.original, "original", "owner-media")

    def test_unknown_profile_rejected(self):
        with self.assertRaises(CatalogError):
            VisualRequest("Another_Game", "tile.a", "0.1.0", 1, 1, "x").validate()

    def test_provider_registry_declares_nonbillable_manual_only(self):
        self.assertEqual(self.registry.get("manual_file").billable, False)
        self.assertEqual(self.registry.available()[1]["status"], "NOT_INSTALLED_OR_AUTHORIZED")


if __name__ == "__main__":
    unittest.main()

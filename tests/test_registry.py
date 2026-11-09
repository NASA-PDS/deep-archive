# encoding: utf-8
"""PDS AIP-GEN: Unit tests of the registry-based archive generator"""
import re
import unittest
from typing import Any
from unittest import mock

from pds2.aipgen import registry

_SERVER = "https://example.invalid/api/search/1"
_BUNDLE = "urn:nasa:pds:testbundle::1.0"
_DATA_LID = "urn:nasa:pds:testbundle:data"
_DATA_LIDVID = f"{_DATA_LID}::2.0"
_BROWSE_LID = "urn:nasa:pds:testbundle:browse"
_BROWSE_LIDVID = f"{_BROWSE_LID}::3.0"


def _product(lidvid: str, name: str) -> dict[str, Any]:
    """Make a minimal registry product with a label file and one data file."""
    return {
        "id": lidvid,
        "title": name,
        "properties": {
            registry._proplabelurl: [f"https://example.invalid/{name}.xml"],
            registry._proplabelmd5: [f"md5-{name}-label"],
            registry._propdataurl: [f"https://example.invalid/{name}.dat"],
            registry._propdatamd5: [f"md5-{name}-data"],
        },
    }


class _Response:
    """A stand-in for ``requests.Response``."""

    def __init__(self, status_code: int, payload: Any = None):
        """Initialize with an HTTP ``status_code`` and a JSON-able ``payload``."""
        self.status_code = status_code
        self._payload = payload
        self.text = ""

    @property
    def ok(self) -> bool:
        """Say whether the status code is a success."""
        return self.status_code < 400

    def json(self) -> Any:
        """Return the payload."""
        return self._payload

    def raise_for_status(self):
        """Complain if the response was not OK."""
        raise ValueError(f"HTTP {self.status_code}")


class _FakeRegistry:
    """A fake PDS API session serving canned bundles, collections, and products."""

    def __init__(self, bundle_props: dict[str, Any], latest: dict[str, str], members: dict[str, list[str]]):
        """Initialize with the bundle properties, the LID → latest LIDVID map, and collection members."""
        self.bundle_props = bundle_props
        self.latest = latest
        self.members = members
        self.calls: list[tuple[str, dict]] = []

    def get(self, url: str, params: dict | None = None) -> _Response:
        """Serve a GET request."""
        params = params or {}
        self.calls.append((url, params))
        path = url[len(_SERVER):]
        if path == "/products":  # Batch collection query
            wanted = re.findall(r'lidvid eq "([^"]+)"', params["q"])
            return _Response(200, {"data": [_product(i, i.split(":")[-3]) for i in wanted]})
        if path.endswith("/members"):
            lidvid = path[len("/products/"):-len("/members")]
            return _Response(200, {"data": [_product(i, i.split(":")[-1]) for i in self.members.get(lidvid, [])]})
        ident = path[len("/products/"):]
        if ident == _BUNDLE:
            bundle = _product(_BUNDLE, "bundle")
            bundle["properties"].update(self.bundle_props)
            return _Response(200, bundle)
        if ident in self.latest:
            return _Response(200, {"id": self.latest[ident], "properties": {"lidvid": [self.latest[ident]]}})
        return _Response(404)

    def count(self, suffix: str) -> int:
        """Count the requests made to URLs ending with ``suffix``."""
        return len([u for u, _ in self.calls if u.endswith(suffix)])


class RegistryCollectionTest(unittest.TestCase):
    """Test discovery of a bundle's collections in the registry."""

    def _run(self, fake: _FakeRegistry) -> dict:
        with mock.patch.object(registry, "_get_session_with_retry", return_value=fake):
            bac, _ = registry._comprehendregistry(_SERVER, _BUNDLE)
        return bac

    def test_lid_only_bundle(self):
        """A bundle with only ``ref_lid_collection`` resolves the latest collection and gathers its products."""
        fake = _FakeRegistry(
            {"ref_lidvid_collection": ["null"], "ref_lid_collection": [_DATA_LID]},
            {_DATA_LID: _DATA_LIDVID},
            {_DATA_LIDVID: [f"{_DATA_LID}:p1::1.0", f"{_DATA_LID}:p2::1.0"]},
        )
        bac = self._run(fake)
        self.assertEqual({_BUNDLE, _DATA_LIDVID, f"{_DATA_LID}:p1::1.0", f"{_DATA_LID}:p2::1.0"}, set(bac))
        self.assertEqual(1, fake.count(f"/products/{_DATA_LID}"))

    def test_lidvid_only_bundle(self):
        """A bundle with only ``ref_lidvid_collection`` behaves as before and never resolves a LID."""
        fake = _FakeRegistry(
            {"ref_lidvid_collection": [_DATA_LIDVID]},
            {},
            {_DATA_LIDVID: [f"{_DATA_LID}:p1::1.0"]},
        )
        bac = self._run(fake)
        self.assertEqual({_BUNDLE, _DATA_LIDVID, f"{_DATA_LID}:p1::1.0"}, set(bac))
        self.assertEqual(0, fake.count(f"/products/{_DATA_LID}"))

    def test_mixed_references(self):
        """A LID in both fields is not resolved or fetched twice; an extra LID is resolved."""
        fake = _FakeRegistry(
            {"ref_lidvid_collection": [_DATA_LIDVID], "ref_lid_collection": [_DATA_LID, _BROWSE_LID]},
            {_DATA_LID: _DATA_LIDVID, _BROWSE_LID: _BROWSE_LIDVID},
            {},
        )
        bac = self._run(fake)
        self.assertEqual({_BUNDLE, _DATA_LIDVID, _BROWSE_LIDVID}, set(bac))
        self.assertEqual(0, fake.count(f"/products/{_DATA_LID}"))
        self.assertEqual(1, fake.count(f"/products/{_BROWSE_LID}"))
        self.assertEqual(1, fake.count(f"/products/{_DATA_LIDVID}/members"))
        batch_queries = [p["q"] for u, p in fake.calls if u == f"{_SERVER}/products"]
        self.assertEqual(1, len(batch_queries))
        self.assertEqual(1, batch_queries[0].count(_DATA_LIDVID))

    def test_no_collections(self):
        """A bundle with no collection references logs an error and yields only the bundle."""
        fake = _FakeRegistry({"ref_lidvid_collection": ["null"]}, {}, {})
        with self.assertLogs(registry._logger, level="ERROR") as logs:
            bac = self._run(fake)
        self.assertEqual({_BUNDLE}, set(bac))
        self.assertTrue(any("No collections" in line for line in logs.output))

    def test_lid_not_found(self):
        """A LID that the registry doesn't know logs a warning; other collections are still gathered."""
        fake = _FakeRegistry(
            {"ref_lid_collection": [_DATA_LID, _BROWSE_LID]},
            {_BROWSE_LID: _BROWSE_LIDVID},
            {},
        )
        with self.assertLogs(registry._logger, level="WARNING") as logs:
            bac = self._run(fake)
        self.assertEqual({_BUNDLE, _BROWSE_LIDVID}, set(bac))
        self.assertTrue(any(_DATA_LID in line and "cannot be found" in line for line in logs.output))

    def test_getlatestlidvid_not_found(self):
        """Resolving an unknown LID returns ``None``."""
        fake = _FakeRegistry({}, {}, {})
        with mock.patch.object(registry, "_get_session_with_retry", return_value=fake):
            with self.assertLogs(registry._logger, level="WARNING"):
                self.assertIsNone(registry._getlatestlidvid(_SERVER, _DATA_LID))

    def test_getlatestlidvid_found(self):
        """Resolving a known LID returns the full LIDVID and asks only for the ``lidvid`` field."""
        fake = _FakeRegistry({}, {_DATA_LID: _DATA_LIDVID}, {})
        with mock.patch.object(registry, "_get_session_with_retry", return_value=fake):
            self.assertEqual(_DATA_LIDVID, registry._getlatestlidvid(_SERVER, _DATA_LID))
        self.assertEqual({"fields": "lidvid"}, fake.calls[0][1])


if __name__ == "__main__":
    unittest.main()

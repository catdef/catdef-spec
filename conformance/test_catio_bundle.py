"""
catdef Conformance: CATIO bundled-transport tests (CA-001).

Per CATIO_SPEC.md §Bundled Transport (ZIP) §Outer-archive extension:

- A ZIP-packaged catio bundle SHOULD use the catdef content-extension
  on the outer archive — .opencatalog for a full catalog, .openthing
  for a single thing.
- Importers MUST accept ZIP-packaged files with either of these two
  catdef extensions.
- Importers SHOULD also accept .zip outer files whose root contains a
  single catdef JSON document, for compatibility.
- Importers identify packaging by content-sniffing the first bytes
  (PK ZIP signature vs raw JSON).
- Raw-JSON catdef files continue to use the canonical extensions
  (.opencatalog, .openthing, .catdef) per document role.

The reference importer implemented here (read_catio) embodies the
normative behavior; ft-catio-* tests exercise it against ZIP-packaged
and raw-JSON fixtures.

ZIP fixtures are built at test time rather than committed as binaries,
so the repo stays text-only.
"""

import io
import json
import zipfile
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _load_raw(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Reference importer — content-sniffs packaging; resolves photos from bundle.
# ---------------------------------------------------------------------------

CATDEF_EXTS_PREFERENCE = (".opencatalog", ".openthing", ".catdef")


def read_catio(path: Path) -> tuple[dict, dict[str, bytes]]:
    """Read a catio document by content-sniffing the packaging.

    Returns (catdef_json, attached_media). attached_media is a dict mapping
    filename → bytes for media files found in the bundle (e.g., photos/watch.jpg
    keyed as "photos/watch.jpg"). For raw-JSON documents the attached_media
    dict is empty.

    Per CATIO_SPEC.md §Rules, if multiple JSON documents exist at a ZIP
    root, the importer uses the first .opencatalog, then .openthing, then
    .catdef.
    """
    with open(path, "rb") as f:
        header = f.read(4)
    if header[:2] == b"PK":
        return _read_zip_bundle(path)
    # Raw JSON — outer extension is advisory, content-sniff decides.
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f), {}


def _read_zip_bundle(path: Path) -> tuple[dict, dict[str, bytes]]:
    with zipfile.ZipFile(path) as zf:
        root_names = [n for n in zf.namelist() if "/" not in n.rstrip("/")]
        chosen = None
        for ext in CATDEF_EXTS_PREFERENCE:
            for name in root_names:
                if name.endswith(ext):
                    chosen = name
                    break
            if chosen:
                break
        if not chosen:
            raise ValueError(f"No catdef JSON document at ZIP root of {path}")
        with zf.open(chosen) as jf:
            data = json.load(jf)
        media: dict[str, bytes] = {}
        for name in zf.namelist():
            if name.startswith("photos/") and not name.endswith("/"):
                with zf.open(name) as mf:
                    media[name] = mf.read()
        return data, media


# ---------------------------------------------------------------------------
# Fixture construction — build ZIP bundles at test time.
# ---------------------------------------------------------------------------

PHOTO_JPEG_STUB = b"\xff\xd8\xff\xe0" + b"JPEG-placeholder-content" * 8  # not a real JPEG, but non-empty


def _build_zip_bundle(dst_path: Path, catdef_json: dict, photo_bytes: bytes) -> None:
    """Build a ZIP bundle at dst_path containing catalog.opencatalog and photos/watch.jpg."""
    with zipfile.ZipFile(dst_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("catalog.opencatalog", json.dumps(catdef_json, indent=2))
        zf.writestr("photos/watch.jpg", photo_bytes)


@pytest.fixture
def bundles(tmp_path):
    """Build three byte-identical bundles at test time:

    - valid_bundle_opencatalog_ext.opencatalog
    - valid_bundle_zip_ext.zip
    - valid_raw_opencatalog.opencatalog (copied from fixtures/ to tmp_path)

    The two ZIP bundles share identical content; only the outer extension differs.
    """
    catdef_json = _load_raw("valid_raw_opencatalog.opencatalog")

    opencatalog_bundle = tmp_path / "valid_bundle_opencatalog_ext.opencatalog"
    zip_bundle = tmp_path / "valid_bundle_zip_ext.zip"

    _build_zip_bundle(opencatalog_bundle, catdef_json, PHOTO_JPEG_STUB)
    _build_zip_bundle(zip_bundle, catdef_json, PHOTO_JPEG_STUB)

    # Raw JSON fixture — copy by reading bytes.
    raw_src = FIXTURES / "valid_raw_opencatalog.opencatalog"
    raw_dst = tmp_path / "valid_raw_opencatalog.opencatalog"
    raw_dst.write_bytes(raw_src.read_bytes())

    return {
        "opencatalog_bundle": opencatalog_bundle,
        "zip_bundle": zip_bundle,
        "raw": raw_dst,
    }


# ---------------------------------------------------------------------------
# ft-catio-01 through ft-catio-05
# ---------------------------------------------------------------------------


class TestCatioBundleExtensions:

    def test_ft_catio_01_opencatalog_outer_extension_accepted(self, bundles):
        """A ZIP with .opencatalog outer extension is accepted and photos/watch.jpg resolves."""
        data, media = read_catio(bundles["opencatalog_bundle"])
        assert data.get("catdef") == "1.4"
        assert data.get("product", {}).get("slug") == "raw-opencatalog"
        assert "photos/watch.jpg" in media
        assert len(media["photos/watch.jpg"]) > 0

    def test_ft_catio_02_zip_outer_extension_accepted_compatibility(self, bundles):
        """A ZIP with .zip outer extension is accepted under the SHOULD-accept rule."""
        data, media = read_catio(bundles["zip_bundle"])
        assert data.get("catdef") == "1.4"
        assert "photos/watch.jpg" in media

    def test_ft_catio_03_raw_opencatalog_accepted(self, bundles):
        """A raw-JSON .opencatalog (no ZIP) is accepted — no content-sniffing error."""
        data, media = read_catio(bundles["raw"])
        assert data.get("catdef") == "1.4"
        # Raw JSON has no attached media.
        assert media == {}

    def test_ft_catio_04_identical_content_identical_state(self, bundles):
        """Byte-identical ZIP contents under different outer extensions produce
        byte-identical parsed catalog state. Content-sniffing is the
        authoritative discriminator — the extension is just a signal.
        """
        data_oc, media_oc = read_catio(bundles["opencatalog_bundle"])
        data_zip, media_zip = read_catio(bundles["zip_bundle"])
        assert data_oc == data_zip
        assert media_oc == media_zip

    def test_ft_catio_05_importer_that_rejects_opencatalog_zip_is_non_conformant(self, bundles):
        """An importer that rejected .opencatalog solely because it's ZIP
        (rather than raw JSON) would be non-conformant. We demonstrate by
        showing that our reference importer correctly opens the ZIP via
        content-sniff — the PK signature is the authoritative discriminator.
        """
        # Sanity: the file really is a ZIP at the byte level.
        with open(bundles["opencatalog_bundle"], "rb") as f:
            header = f.read(2)
        assert header == b"PK", (
            "fixture precondition: .opencatalog bundle must be a ZIP for this test")
        # And the importer accepts it. An importer that threw here on
        # extension-shape alone would fail ft-catio-05.
        data, media = read_catio(bundles["opencatalog_bundle"])
        assert data.get("catdef") == "1.4"


class TestCatioEdgeCases:
    """Supporting edge cases — not numbered ft-* tests, but document behavior."""

    def test_zip_with_multiple_json_at_root_prefers_opencatalog(self, tmp_path):
        """Per Rule 1 preference order: .opencatalog > .openthing > .catdef."""
        oc_json = {"catdef": "1.4", "product": {"name": "oc", "slug": "oc"}, "templates": []}
        ot_json = {"catdef": "1.4", "product": {"name": "ot", "slug": "ot"}, "templates": []}
        dst = tmp_path / "multi-root.opencatalog"
        with zipfile.ZipFile(dst, "w") as zf:
            zf.writestr("schema.catdef", json.dumps({"catdef": "1.4", "templates": []}))
            zf.writestr("single.openthing", json.dumps(ot_json))
            zf.writestr("catalog.opencatalog", json.dumps(oc_json))
        data, _ = read_catio(dst)
        # Preference order: .opencatalog wins.
        assert data.get("product", {}).get("slug") == "oc"

    def test_zip_missing_catdef_json_errors(self, tmp_path):
        dst = tmp_path / "bad.opencatalog"
        with zipfile.ZipFile(dst, "w") as zf:
            zf.writestr("photos/watch.jpg", b"PHOTO")
            zf.writestr("notes.txt", b"not a catdef")
        with pytest.raises(ValueError, match="No catdef JSON document"):
            read_catio(dst)

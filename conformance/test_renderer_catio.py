"""
catdef Conformance: the SHIPPED reference renderer must implement CATIO
bundled transport (CA-017 / catdef-spec#45).

Why this file exists, separately from test_catio_bundle.py:

test_catio_bundle.py proves the CATIO bundled-transport rules are
*implementable* — it exercises a Python reference importer (``read_catio``)
defined inside that test file. It does not prove that the artifact catdef
actually ships implements them. For 158 days it did not: the reference
renderer could not open the canonical reference catalog, which is itself a
ZIP bundle, while the suite stayed green. The renderer sat outside the
standard that governs it.

These tests close that gap by executing the renderer's own loader code,
extracted verbatim from ``renderer/index.html`` between the
``CATIO-LOADER-BEGIN`` / ``CATIO-LOADER-END`` markers, under Node. No
re-implementation is permitted here: assertions live in Python, execution
happens in the shipped JavaScript, and
``conformance/renderer_catio_driver.cjs`` only reports what that code did.

Node provides ``DecompressionStream('deflate-raw')`` natively (Node 18+), so
this needs no browser and no third-party dependency. The browser floor for
the same API is Chrome 103+, Firefox 113+, Safari 16.4+.
"""

import json
import shutil
import struct
import subprocess
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER = REPO_ROOT / "renderer" / "index.html"
DRIVER = Path(__file__).parent / "renderer_catio_driver.cjs"
CANONICAL = REPO_ROOT / "canonical" / "riverside-heritage-reference-v1.4.opencatalog"

BEGIN_MARKER = "// ==== CATIO-LOADER-BEGIN ===="
END_MARKER = "// ==== CATIO-LOADER-END ===="

NODE = shutil.which("node")
requires_node = pytest.mark.skipif(
    NODE is None,
    reason=(
        "node not on PATH — the shipped renderer's CATIO loader is NOT "
        "exercised by this run. test_loader_block_present still guards the "
        "block's existence without Node."
    ),
)


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def extract_loader_source() -> str:
    """Pull the CATIO loader block out of the shipped renderer."""
    html = RENDERER.read_text(encoding="utf-8")
    start = html.find(BEGIN_MARKER)
    end = html.find(END_MARKER)
    assert start != -1, (
        f"{BEGIN_MARKER} missing from renderer/index.html — the CATIO loader "
        "has been removed or its markers renamed. CATIO_SPEC.md §Bundled "
        "Transport makes accepting ZIP bundles a MUST; see CA-017."
    )
    assert end > start, f"{END_MARKER} missing or out of order in renderer/index.html"
    return html[start + len(BEGIN_MARKER) : end]


# ---------------------------------------------------------------------------
# Fixture construction — built at test time, per the convention established
# in test_catio_bundle.py, so the repo stays text-only.
# ---------------------------------------------------------------------------


def _catalog_doc(item_photos):
    return {
        "catio": "1.0",
        "catdef": "1.4",
        "type": "catalog",
        "product": {"name": "Renderer CATIO Test", "slug": "renderer-catio-test"},
        "templates": [
            {
                "name": "Widget",
                "field_defs": [
                    {"label": "Title", "type": "String", "sort_order": 10},
                    {"label": "Photos", "type": "Photo", "sort_order": 20, "multi": True},
                ],
            }
        ],
        "data": {
            "items": [
                {
                    "template": "Widget",
                    "fields": {"Title": f"Widget {i + 1}", "Photos": photos},
                }
                for i, photos in enumerate(item_photos)
            ]
        },
    }


def _fake_jpeg(seed: bytes, size: int = 4096) -> bytes:
    """Deterministic pseudo-image bytes.

    Real JPEG bytes are not needed to prove unpacking is byte-exact — the
    tests compare SHA-256 of what the renderer produced against what was
    packed. Visual verification needs real photos and is done against the
    adopter bundle in a browser, not here.
    """
    body = bytearray(b"\xff\xd8\xff\xe0")
    while len(body) < size:
        body.extend(seed)
        body.extend(bytes((len(body) % 251,)))
    return bytes(body[:size])


def _write_bundle(path: Path, doc: dict, photos: dict, method_for):
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(
            zipfile.ZipInfo("catalog.opencatalog"),
            json.dumps(doc),
            compress_type=method_for("catalog.opencatalog"),
        )
        for name, blob in photos.items():
            zf.writestr(
                zipfile.ZipInfo(f"photos/{name}"),
                blob,
                compress_type=method_for(name),
            )


@pytest.fixture(scope="module")
def bundles(tmp_path_factory):
    """Build the bundle fixtures once per module."""
    out = tmp_path_factory.mktemp("catio-renderer")
    made = {}

    photos = {
        "alpha.jpg": _fake_jpeg(b"alpha"),
        "beta.jpg": _fake_jpeg(b"beta", 9001),
        "gamma.jpg": _fake_jpeg(b"gamma", 1234),
    }
    doc = _catalog_doc(
        [
            [{"filename": "alpha.jpg", "slot": 1, "is_primary": True}],
            [
                {"filename": "beta.jpg", "slot": 1, "is_primary": True},
                {"filename": "gamma.jpg", "slot": 2, "caption": "Detail"},
            ],
        ]
    )

    # All-stored: no DecompressionStream involvement at all.
    p = out / "stored.opencatalog"
    _write_bundle(p, doc, photos, lambda _n: zipfile.ZIP_STORED)
    made["stored"] = (p, doc, photos)

    # All-deflated: the canonical reference bundle's shape (24/24 deflated).
    p = out / "deflated.opencatalog"
    _write_bundle(p, doc, photos, lambda _n: zipfile.ZIP_DEFLATED)
    made["deflated"] = (p, doc, photos)

    # Mixed: the adopter's shape — {deflate: 1 (the JSON), stored: N}.
    p = out / "mixed.opencatalog"
    _write_bundle(
        p,
        doc,
        photos,
        lambda n: zipfile.ZIP_DEFLATED if n.endswith(".opencatalog") else zipfile.ZIP_STORED,
    )
    made["mixed"] = (p, doc, photos)

    # Raw JSON — the path that already worked and must not regress.
    p = out / "raw.opencatalog"
    p.write_text(json.dumps(doc), encoding="utf-8")
    made["raw"] = (p, doc, {})

    # .openthing alongside .opencatalog at the root: Rule 1 preference order.
    p = out / "preference.opencatalog"
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("aaa.openthing", json.dumps({"catdef": "1.4", "type": "thing"}))
        zf.writestr("catalog.opencatalog", json.dumps(doc))
    made["preference"] = (p, doc, {})

    # A ZIP with no catdef document at the root.
    p = out / "not-catio.opencatalog"
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("readme.txt", "no catdef document here")
    made["not_catio"] = (p, None, {})

    # Local headers zeroed with a data-descriptor flag set, real values left
    # in the central directory. This is what a streaming exporter writes, and
    # it is why the loader must trust the central directory. A loader reading
    # local-header sizes returns empty members here and fails.
    p = out / "data-descriptor.opencatalog"
    src = (out / "deflated.opencatalog").read_bytes()
    buf = bytearray(src)
    offset = 0
    while True:
        offset = buf.find(b"PK\x03\x04", offset)
        if offset == -1:
            break
        flags = struct.unpack_from("<H", buf, offset + 6)[0]
        struct.pack_into("<H", buf, offset + 6, flags | 0x08)  # bit 3
        struct.pack_into("<III", buf, offset + 14, 0, 0, 0)  # crc, csize, usize
        offset += 4
    p.write_bytes(bytes(buf))
    made["data_descriptor"] = (p, doc, photos)

    return made


# ---------------------------------------------------------------------------
# Node execution
# ---------------------------------------------------------------------------


def run_loader(tmp_path: Path, cases) -> dict:
    """Execute the SHIPPED loader against the given cases."""
    loader_js = tmp_path / "shipped_catio_loader.cjs"
    loader_js.write_text(extract_loader_source(), encoding="utf-8")

    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"cases": [{"name": n, "path": str(p)} for n, p in cases]}),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [NODE, str(DRIVER), str(loader_js), str(manifest)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"driver exited {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    payload = json.loads(proc.stdout)
    return {r["name"]: r for r in payload["results"]}


# ---------------------------------------------------------------------------
# ft-renderer-catio-* — the shipped renderer against CATIO bundled transport
# ---------------------------------------------------------------------------


def test_loader_block_present():
    """ft-renderer-catio-01: the shipped renderer carries a CATIO loader.

    Pure Python on purpose. This is the one guard that cannot be silently
    skipped by a machine without Node, so removing bundle support from
    renderer/index.html always fails the suite somewhere.
    """
    source = extract_loader_source()
    assert len(source.strip()) > 500, "CATIO loader block is suspiciously small"
    # Match the constructor call itself, not the substring: "deflate-raw" also
    # appears in the loader's error messages, so a bare substring check stays
    # green even when the call is changed to the wrong (zlib-wrapped) variant.
    assert "DecompressionStream('deflate-raw')" in source, (
        "loader must construct DecompressionStream('deflate-raw') — ZIP method "
        "8 stores raw deflate, and 'deflate' fails on every compressed member"
    )
    assert "0x06054b50" in source, (
        "loader must locate the end-of-central-directory record; local headers "
        "are not authoritative for sizes in stream-written ZIPs"
    )
    # Keeping the block DOM-free is what makes it extractable and testable.
    for forbidden in ("document.", "window.", "$(", "URL.createObjectURL"):
        assert forbidden not in source, (
            f"CATIO loader block must stay DOM-free (found {forbidden!r}); "
            "DOM glue belongs outside the markers or this test cannot run it"
        )


def test_renderer_stays_single_file_and_classic():
    """ft-renderer-catio-09: L1 self-host invariants (value #1, L1 is sacred).

    Pure Python. Bundle support must not be bought with an L1 regression:

    - ``type="module"`` is CORS-blocked over ``file://``, so a module script
      would make the renderer work when served and fail silently when opened
      as a local file — the one configuration L1 exists to guarantee.
    - An external ``<script src>`` breaks self-host path 1 in renderer/README
      (download index.html, open it), because the sibling file would not come
      along.
    - The build number is mandated on every page by the shared project
      principles so a deployed build is identifiable from a screen capture;
      its absence is why establishing deployment currency for CA-017 needed a
      byte-size comparison.
    """
    html = RENDERER.read_text(encoding="utf-8")
    assert 'type="module"' not in html, (
        "renderer must not use an ES module: modules are CORS-blocked over "
        "file://, which breaks the browser-only no-server L1 path"
    )
    import re

    assert not re.search(r"<script[^>]+\bsrc=", html), (
        "renderer must stay a single self-contained file: an external script "
        "src breaks the download-and-open self-host path in renderer/README.md"
    )
    assert 'class="build-number"' in html, (
        "renderer must display a build number (shared project principles)"
    )


@requires_node
def test_shipped_renderer_sniffs_and_unpacks(tmp_path, bundles):
    """ft-renderer-catio-02: PK sniffing, all three compression shapes."""
    cases = [(name, bundles[name][0]) for name in ("stored", "deflated", "mixed", "raw")]
    results = run_loader(tmp_path, cases)

    for name in ("stored", "deflated", "mixed"):
        r = results[name]
        assert r["ok"], f"{name}: {r.get('error')}"
        assert r["sniffed_zip"] is True, f"{name}: PK signature not detected"
        assert r["document_name"] == "catalog.opencatalog"
        assert r["item_count"] == 2
        assert r["catio_version"] == "1.0"
        assert r["media_names"] == ["alpha.jpg", "beta.jpg", "gamma.jpg"]

    # Raw JSON must still work — content-sniffing must not regress the path
    # that worked before bundles were supported.
    raw = results["raw"]
    assert raw["ok"], raw.get("error")
    assert raw["sniffed_zip"] is False
    assert raw["item_count"] == 2
    assert raw["media_names"] == []


@requires_node
def test_unpacked_media_is_byte_exact(tmp_path, bundles):
    """ft-renderer-catio-03: unpacked photo bytes match what was packed."""
    import hashlib

    cases = [(name, bundles[name][0]) for name in ("stored", "deflated", "mixed")]
    results = run_loader(tmp_path, cases)

    for name in ("stored", "deflated", "mixed"):
        _path, _doc, photos = bundles[name]
        got = results[name]["media_sha256"]
        for filename, blob in photos.items():
            expected = hashlib.sha256(blob).hexdigest()
            assert got[filename] == expected, (
                f"{name}/{filename}: unpacked bytes differ from packed bytes"
            )
            assert got[f"{filename}::len"] == len(blob)


@requires_node
def test_media_keyed_by_bare_filename(tmp_path, bundles):
    """ft-renderer-catio-04: CATIO Rule 2 — filename-only resolution.

    References in the JSON carry no path prefix, so every reference must
    resolve against the unpacked media map.
    """
    results = run_loader(tmp_path, [("mixed", bundles["mixed"][0])])
    r = results["mixed"]
    assert r["ok"], r.get("error")
    assert r["photo_refs"] == ["alpha.jpg", "beta.jpg", "gamma.jpg"]
    assert r["unresolved_refs"] == [], (
        "every filename-only photo reference must resolve to a bundle member"
    )


@requires_node
def test_root_document_preference(tmp_path, bundles):
    """ft-renderer-catio-05: Rule 1 — .opencatalog wins over .openthing."""
    results = run_loader(tmp_path, [("preference", bundles["preference"][0])])
    r = results["preference"]
    assert r["ok"], r.get("error")
    assert r["document_name"] == "catalog.opencatalog"
    assert r["item_count"] == 2


@requires_node
def test_central_directory_is_authoritative(tmp_path, bundles):
    """ft-renderer-catio-06: data-descriptor ZIPs read correctly.

    A streaming exporter may write zeros for crc/sizes in the local header
    and put the real values in a trailing data descriptor. A loader that
    trusts local headers silently returns empty members for exactly the
    archives an exporter is most likely to produce.
    """
    import hashlib

    results = run_loader(tmp_path, [("dd", bundles["data_descriptor"][0])])
    r = results["dd"]
    assert r["ok"], r.get("error")
    assert r["item_count"] == 2
    _path, _doc, photos = bundles["data_descriptor"]
    for filename, blob in photos.items():
        assert r["media_sha256"][filename] == hashlib.sha256(blob).hexdigest()


@requires_node
def test_non_catio_zip_reports_clearly(tmp_path, bundles):
    """ft-renderer-catio-07: a ZIP with no root catdef document fails loudly."""
    results = run_loader(tmp_path, [("not_catio", bundles["not_catio"][0])])
    r = results["not_catio"]
    assert r["ok"] is False
    assert "root" in r["error"].lower() or "catio" in r["error"].lower(), (
        f"error should name the missing root document, got: {r['error']!r}"
    )


@requires_node
@pytest.mark.skipif(not CANONICAL.exists(), reason="canonical reference artifact absent")
def test_shipped_renderer_reads_canonical_reference_bundle(tmp_path):
    """ft-renderer-catio-08: the reference renderer reads the reference catalog.

    This is the headline assertion of CA-017. The canonical artifact is itself
    a CATIO bundle (24 members, all deflated), so before this work the
    reference implementation could not open the reference data.
    """
    results = run_loader(tmp_path, [("canonical", CANONICAL)])
    r = results["canonical"]
    assert r["ok"], f"canonical reference bundle failed to load: {r.get('error')}"
    assert r["sniffed_zip"] is True
    assert r["document_name"] == "catalog.opencatalog"
    assert r["catdef_version"] == "1.4"
    assert r["item_count"] == 12
    assert len(r["media_names"]) == 23, (
        f"expected 23 bundled photos, got {len(r['media_names'])}"
    )
    assert r["unresolved_refs"] == [], (
        "every photo reference in the canonical catalog must resolve: "
        f"unresolved={r['unresolved_refs']}"
    )

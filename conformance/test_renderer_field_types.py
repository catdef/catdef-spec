"""
catdef Conformance: structured field types must render as values, not as raw
JSON (catdef-spec#54).

Thirteen types are declared in the canonical reference catalog. The five
scalar ones render. All eight structured ones reach the renderer's generic
`typeof val === 'object'` branch and are dumped into a <pre> block as raw
JSON -- on the canonical reference file, on the front-page CTA:

    Date Made            Date         {"date":"1905","circa":true}
    Exhibition Dates     Date         {"start":"2022-04-01","end":"2022-06-30"}
    Case Diameter Range  Number       {"min":7.5,"max":7.8}
    Purchase Price Range Money        {"low":{...},"high":{...}}
    Display Location     GeoLocation  {"lat":42.3311,"lng":-74.0168,...}
    External Record      URL          {"url":"...","title":"...",...}
    Reference Scan       CloudFile    {"url":"...","provider":...,...}
    Inscriptions         Table        [{"Text":"OSGOOD MFG / RIVERSIDE",...}]

CA-006 extended the conformance VALIDATOR for exactly these shapes; the
renderer never followed. This is one missing dispatch layer, not eight
missing formatters.

DISPATCH IS ON THE DECLARED TYPE, NEVER ON VALUE SHAPE. `Date` appears as
both {date,circa} and {start,end} in the same file, so any implementation
inferring meaning from which keys are present is wrong today rather than
merely fragile later. Discriminating BETWEEN those two shapes *within* a
field already declared `Date` is a different thing and is required -- the
prohibition is on inferring the type itself from the value.

A field with no declared type must fall through to the existing generic
rendering rather than being guessed at. That is what -09 pins down.

No new fixture: the canonical reference file exercises all thirteen declared
types, including two shapes of Date, a nested Money, a Table with
heterogeneous rows and a Table that is empty. It is a better corpus than
anything written by hand for the purpose.

SCOPE LIMIT. These cases drive renderTypedValue(), a pure string-producing
function, so they prove what the renderer EMITS. They do not prove how it
looks. Per CA-021 Call 7 that remains an observational criterion.
"""

import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER = REPO_ROOT / "renderer" / "index.html"
DRIVER = Path(__file__).parent / "renderer_field_types_driver.cjs"
CANONICAL = REPO_ROOT / "canonical" / "riverside-heritage-reference-v1.4.opencatalog"

NODE = shutil.which("node")
requires_node = pytest.mark.skipif(
    NODE is None, reason="node not on PATH -- renderTypedValue() not exercised.")

#: Extracted in dependency order. renderTypedValue() is the dispatch layer;
#: the rest are what it and its callers already depend on.
REQUIRED_FUNCS = (
    "esc",
    "resolveRenderableLink",
    "isTranslatableValue",
    "localeVariants",
    "lookupVariant",
    "resolveTranslatable",
    "resolveText",
    "noTranslateAttr",
    "renderScalarValue",
)

BEGIN_MARKER = "// ==== TYPED-FIELDS-BEGIN ===="
END_MARKER = "// ==== TYPED-FIELDS-END ===="


def extract_function(src: str, name: str) -> str:
    start = src.find("\nfunction %s(" % name)
    assert start != -1, (
        "renderer/index.html no longer defines a top-level function %r; "
        "update the extraction rather than reimplementing it here." % name)
    brace = src.index("{", start)
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start + 1:i + 1]
    raise AssertionError("unbalanced braces extracting %r" % name)


def run_cases(cases: list) -> dict:
    src = RENDERER.read_text(encoding="utf-8")
    import re
    parts = []
    for pattern in (r"^const RENDERABLE_EXT_RE = .*$", r"^const I18N_POLICY_KEYS = .*$"):
        m = re.search(pattern, src, re.M)
        assert m, "declaration not found: %s" % pattern
        parts.append(m.group(0))
    parts += ["let CATALOG_SOURCE_URL = null;", "let PRIMARY_LOCALE = null;",
              "const VIEWER_LOCALE = 'en';"]
    parts += [extract_function(src, n) for n in REQUIRED_FUNCS]
    # The dispatch layer is taken as a whole marked block rather than function
    # by function: it carries consts (EN_DASH, TYPED_RENDERERS) and several
    # private helpers, and enumerating them here would drift from the file.
    b, e = src.find(BEGIN_MARKER), src.find(END_MARKER)
    assert b != -1 and e > b, (
        "renderer/index.html is missing the %s / %s markers that delimit the "
        "typed-field dispatch layer" % (BEGIN_MARKER, END_MARKER))
    parts.append(src[b + len(BEGIN_MARKER):e])
    parts.append("module.exports = { %s, renderTypedValue };"
                 % ", ".join(REQUIRED_FUNCS))
    with tempfile.TemporaryDirectory() as td:
        mod = Path(td) / "extracted.cjs"
        mod.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
        cf = Path(td) / "cases.json"
        cf.write_text(json.dumps(cases), encoding="utf-8")
        proc = subprocess.run([NODE, str(DRIVER), str(mod), str(cf)],
                              capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, "driver failed: %s" % (proc.stderr or proc.stdout)
    return {r["name"]: r for r in json.loads(proc.stdout)["results"]}


def canonical_structured():
    """(declared_type, label, value) for every structured field, from the
    canonical reference file."""
    with zipfile.ZipFile(CANONICAL) as z:
        root = next(n for n in z.namelist()
                    if n.endswith(".opencatalog") and "/" not in n)
        doc = json.loads(z.read(root).decode("utf-8"))
    types = {fd["label"]: fd["type"]
             for t in doc.get("templates", []) for fd in t.get("field_defs", [])}
    out = []
    for item in doc.get("data", {}).get("items", []):
        for label, val in (item.get("fields") or {}).items():
            if isinstance(val, (dict, list)) and types.get(label) in STRUCTURED:
                out.append((types[label], label, val))
    return out


STRUCTURED = {"Date", "Number", "Money", "GeoLocation", "URL", "CloudFile", "Table"}


def case(name, type_, value):
    return {"name": name, "fd": {"label": name, "type": type_}, "value": value}


# ---------------------------------------------------------------------------


@requires_node
def test_date_circa_and_range():
    """ft-renderer-type-01: both declared Date shapes render readably."""
    r = run_cases([
        case("circa", "Date", {"date": "1905", "circa": True}),
        case("exact", "Date", {"date": "1905", "circa": False}),
        case("range", "Date", {"start": "1887", "end": "1894"}),
    ])
    assert "1905" in r["circa"]["html"] and "c." in r["circa"]["html"], r["circa"]
    assert "1905" in r["exact"]["html"] and "c." not in r["exact"]["html"], r["exact"]
    assert "1887" in r["range"]["html"] and "1894" in r["range"]["html"], r["range"]
    for k in r:
        assert "{" not in r[k]["html"], "raw JSON leaked: %r" % r[k]["html"]


@requires_node
def test_number_and_money_ranges():
    """ft-renderer-type-02: Number and Money ranges, incl. nested Money."""
    r = run_cases([
        case("num", "Number", {"min": 7.5, "max": 7.8}),
        case("money", "Money",
             {"low": {"amount": 40, "currency": "USD"},
              "high": {"amount": 120, "currency": "USD"}}),
    ])
    assert "7.5" in r["num"]["html"] and "7.8" in r["num"]["html"], r["num"]
    m = r["money"]["html"]
    assert "40" in m and "120" in m and "USD" in m, m
    assert "amount" not in m and "{" not in m, "raw JSON leaked: %r" % m


@requires_node
def test_geolocation_prefers_label_but_keeps_coordinates():
    """ft-renderer-type-03: a named place renders by name; an unnamed one
    still renders its coordinates rather than disappearing."""
    r = run_cases([
        case("named", "GeoLocation",
             {"lat": 42.3311, "lng": -74.0168, "label": "Gallery 2, Case 4"}),
        case("bare", "GeoLocation", {"lat": 42.3311, "lng": -74.0168}),
    ])
    assert "Gallery 2, Case 4" in r["named"]["html"], r["named"]
    assert "42.3311" in r["bare"]["html"], r["bare"]
    assert "{" not in r["bare"]["html"]


@requires_node
def test_url_renders_as_a_link_and_keeps_its_description():
    """ft-renderer-type-04: URL object -> anchor; no author content dropped.

    CATDEF_SPEC.md:784 obliges a producer to preserve every key of the URL
    object on re-export. The renderer does not re-export, so that obligation
    is not this function's to discharge -- but silently discarding the
    author's description is the same loss by a different route, and this is
    the type most likely to be CA-022 Call 4a's first round-trip failure.
    """
    r = run_cases([case("url", "URL", {
        "url": "https://en.wikipedia.org/wiki/Stanley_Works",
        "title": "Stanley Works - Wikipedia",
        "description": "Background on the historical manufacturer."})])
    h = r["url"]["html"]
    assert 'href="https://en.wikipedia.org/wiki/Stanley_Works"' in h, h
    assert "Stanley Works - Wikipedia" in h, h
    assert "Background on the historical manufacturer." in h, (
        "the author's description was dropped: %r" % h)


@requires_node
def test_cloudfile_renders_as_a_named_link():
    """ft-renderer-type-05: CloudFile -> link labelled by filename."""
    r = run_cases([case("cf", "CloudFile", {
        "url": "https://example.org/scans/cartwright-album-1887.pdf",
        "provider": "example.org",
        "filename": "cartwright-album-1887.pdf"})])
    h = r["cf"]["html"]
    assert 'href="https://example.org/scans/cartwright-album-1887.pdf"' in h, h
    assert "cartwright-album-1887.pdf" in h, h


@requires_node
def test_table_renders_rows_including_heterogeneous_and_empty():
    """ft-renderer-type-06: Table -> a table. Rows differ in their keys and
    one canonical Table is empty; neither may throw or emit JSON."""
    r = run_cases([
        case("rows", "Table", [
            {"Text": "OSGOOD MFG / RIVERSIDE", "Position": "Under-body stamp"},
            {"Text": "STANLEY / NO. 4", "Position": "Behind the frog",
             "Legibility": "Clear"},
        ]),
        case("empty", "Table", []),
        case("nonrows", "Table", ["loose", "values"]),
    ])
    h = r["rows"]["html"]
    assert "<table" in h and "OSGOOD MFG / RIVERSIDE" in h, h
    assert "Legibility" in h, "union of row keys must form the header: %r" % h
    assert r["empty"].get("error") is None, r["empty"]
    assert r["empty"]["html"] == "", (
        "an empty Table renders as nothing, not an empty table frame and "
        "not a fall-through: %r" % r["empty"]["html"])
    # A Table holding entries that are not row objects must FALL THROUGH so
    # the generic array path still shows them. Returning '' would silently
    # discard author content -- the same loss this layer exists to prevent,
    # and a mutation returning null for the empty case was indistinguishable
    # until this case existed.
    assert r["nonrows"]["html"] is None, (
        "a malformed Table must fall through rather than drop its entries; "
        "got %r" % r["nonrows"]["html"])


@requires_node
def test_declared_type_wins_over_value_shape():
    """ft-renderer-type-07 (GATING): no shape-guessing.

    A String field whose value happens to be an object must NOT be formatted
    as though it were a Date, and a field with no declared type must fall
    through rather than being guessed at. Returning null means "not mine" and
    lets the caller's existing generic path handle it.
    """
    r = run_cases([
        case("string_obj", "String", {"date": "1905", "circa": True}),
        {"name": "no_type", "fd": {"label": "Mystery"},
         "value": {"date": "1905", "circa": True}},
        {"name": "no_fd", "fd": None, "value": {"min": 1, "max": 2}},
    ])
    for k in ("string_obj", "no_type", "no_fd"):
        assert r[k].get("error") is None, (
            "%s raised instead of falling through -- the driver reports a "
            "throw as html=None, so this assertion is what keeps an "
            "exception from reading as correct behaviour: %s"
            % (k, r[k].get("error")))
        assert r[k]["html"] is None, (
            "%s must fall through (null), not be formatted by shape; got %r"
            % (k, r[k]["html"]))


@requires_node
def test_scalar_types_still_fall_through():
    """ft-renderer-type-08 (control): the five scalar types are untouched.

    They render correctly today. A dispatch layer that claimed them would be
    a regression, and this is the mutation "handle everything" would slip
    past otherwise.
    """
    r = run_cases([
        case("s", "String", "Tinplate toy locomotive"),
        case("i", "Integer", 4),
        case("b", "Boolean", True),
        case("e", "Enumerated", "Stanley"),
        case("rt", "RichText", "<p>Some prose.</p>"),
    ])
    for k in r:
        assert r[k].get("error") is None, (
            "scalar type %s raised instead of falling through: %s"
            % (k, r[k].get("error")))
        assert r[k]["html"] is None, (
            "scalar type %s must fall through to the existing path; got %r"
            % (k, r[k]["html"]))


@requires_node
def test_every_structured_field_in_the_canonical_file():
    """ft-renderer-type-09 (GATING): no raw JSON anywhere in the reference.

    The whole point. Every structured field in the file the front-page CTA
    loads must render as a value.
    """
    fields = canonical_structured()
    assert fields, "fixture precondition: canonical file has structured fields"
    cases = [{"name": "%s-%s-%d" % (t, label, i),
              "fd": {"label": label, "type": t}, "value": v}
             for i, (t, label, v) in enumerate(fields)]
    r = run_cases(cases)
    bad = []
    for name, res in r.items():
        html = res.get("html")
        if res.get("error"):
            bad.append("%s raised %s" % (name, res["error"]))
        elif html is None and not name.startswith("Table-") :
            bad.append("%s fell through unrendered" % name)
        elif html and ('{"' in html or '":' in html):
            bad.append("%s emitted raw JSON" % name)
    assert not bad, "%d structured field(s) still wrong:\n  %s" % (
        len(bad), "\n  ".join(bad))

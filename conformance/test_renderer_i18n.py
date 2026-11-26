"""
catdef Conformance: the SHIPPED reference renderer must honour polymorphic
translatable fields and the `.machine-translate` policy (catdef-spec#53/#52).

Why this file exists, separately from policies/test_i18n_policies.py:

policies/test_i18n_policies.py proves the i18n policy rules are
*implementable*. It does so by defining ``render_to_html()`` -- a conformant
renderer written inside the test file -- and then asserting that function
emits ``translate="no"``. ft-i18n-09 at line 257 of that file asserts the
marker appears "ON DOM NODES" in a module that has no DOM. It passes green.

The shipped renderer emits no such attribute, performs no locale resolution
of any kind, and renders a polymorphic translatable Title as the string
``[object Object]`` -- on the canonical reference file, on the front-page
call-to-action. Per CATDEF_SPEC.md §1392 and value #9 that is a conformance
failure, not a cosmetic bug: the policy is not merely unenforced, it is
unparsed.

This is CA-021 instance 1 in its purest form -- a test that cannot fail for
the artifact it claims to govern, because the artifact is never executed.
test_renderer_catio.py closed that gap for the CATIO bundle path only; the
memo that reported it was titled "harness gap closed", which was broader
than what had been done (CA-021 Call 7).

These tests execute the renderer's OWN field-rendering functions, extracted
verbatim from renderer/index.html, under Node. No re-implementation is
permitted: assertions live in Python, execution happens in the shipped
JavaScript, and renderer_i18n_driver.cjs only reports what that code did.

EXPECTED STATE ON LANDING: RED. These tests are written against the spec,
not against the current renderer, and were observed failing before #52 was
begun. A port that lands green was renamed rather than ported.

Normative basis:
  CATDEF_SPEC.md §1392  .machine-translate: "Never" -> runtime MUST mark the
                        rendered content non-translatable via translate="no"
  CATDEF_SPEC.md §1293  locale variants resolve by RFC 4647 §3.4 (Lookup),
                        falling back to primaryLocale
  CATDEF_SPEC.md §1265  policy compliance is a conformance requirement
"""

import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER = REPO_ROOT / "renderer" / "index.html"
DRIVER = Path(__file__).parent / "renderer_i18n_driver.cjs"
CANONICAL = REPO_ROOT / "canonical" / "riverside-heritage-reference-v1.4.opencatalog"

NODE = shutil.which("node")
requires_node = pytest.mark.skipif(
    NODE is None,
    reason=(
        "node not on PATH -- the shipped renderer's field-rendering path is "
        "NOT exercised by this run. test_renderer_declares_translate_no still "
        "guards the policy's presence without Node."
    ),
)


# ---------------------------------------------------------------------------
# Verbatim extraction from the shipped renderer
# ---------------------------------------------------------------------------

#: Functions the field-rendering path needs, in dependency order. Extracted
#: by name rather than between markers, so the extraction names exactly what
#: it executes and a rename surfaces as an explicit failure here rather than
#: as a silent fallback to something reimplemented in the harness.
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


def extract_function(src: str, name: str) -> str:
    """Return the verbatim source of a top-level `function name(...) {...}`."""
    start = src.find("\nfunction %s(" % name)
    assert start != -1, (
        "renderer/index.html no longer defines a top-level function %r. "
        "If it was renamed or inlined, this extraction must be updated -- "
        "do NOT reimplement it here." % name
    )
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


def build_module() -> str:
    src = RENDERER.read_text(encoding="utf-8")

    consts = []
    for pattern in (
        r"^const RENDERABLE_EXT_RE = .*$",
        r"^const I18N_POLICY_KEYS = .*$",
    ):
        m = re.search(pattern, src, re.M)
        assert m, "declaration not found in renderer: %s" % pattern
        consts.append(m.group(0))
    # Mutable module state the extracted functions close over. PRIMARY_LOCALE
    # is set by loadCatdef() at runtime; these cases pass it via opts instead,
    # so the extracted default is the same `null` a fresh page starts with.
    consts.append("let CATALOG_SOURCE_URL = null;")
    consts.append("let PRIMARY_LOCALE = null;")
    consts.append("const VIEWER_LOCALE = 'en';")

    parts = list(consts) + [extract_function(src, n) for n in REQUIRED_FUNCS]
    exports = "module.exports = { %s };" % ", ".join(REQUIRED_FUNCS)
    return "\n\n".join(parts + [exports]) + "\n"


def run_cases(cases: list, mode: str = "scalar") -> list:
    """Execute the shipped render path over `cases`.

    mode="scalar" drives renderScalarValue(); mode="attr" drives the
    resolveText()/noTranslateAttr() pair the title and alt paths use.
    """
    module_src = build_module()
    with tempfile.TemporaryDirectory() as td:
        mod = Path(td) / "extracted.cjs"
        mod.write_text(module_src, encoding="utf-8")
        cases_file = Path(td) / "cases.json"
        cases_file.write_text(json.dumps(cases), encoding="utf-8")
        proc = subprocess.run(
            [NODE, str(DRIVER), str(mod), str(cases_file), mode],
            capture_output=True, text=True, timeout=60,
        )
    assert proc.returncode == 0, "driver failed: %s" % (proc.stderr or proc.stdout)
    return json.loads(proc.stdout)["results"]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

NEVER_TITLE = {
    ".context": "heritage-catalog",
    ".machine-translate": "Never",
    ".en": "Field-recorded lullaby sheet music",
    ".fr": "Partition de berceuse enregistree sur le terrain",
}

ALLOW_TITLE = {
    ".en": "Carpenter's jack plane",
    ".fr": "Rabot de charpentier",
}


def canonical_never_fields():
    """Every `.machine-translate: "Never"` field in the canonical reference."""
    with zipfile.ZipFile(CANONICAL) as z:
        root = next(n for n in z.namelist()
                    if n.endswith(".opencatalog") and "/" not in n)
        doc = json.loads(z.read(root).decode("utf-8"))
    out = []
    for item in doc.get("data", {}).get("items", []):
        fields = item.get("fields", item)
        for key, val in fields.items():
            if isinstance(val, dict) and val.get(".machine-translate") == "Never":
                out.append((key, val))
    return doc.get("primaryLocale"), out


# ---------------------------------------------------------------------------
# ft-renderer-i18n-01 -- skip-proof floor (pure Python, no Node)
# ---------------------------------------------------------------------------


def test_renderer_declares_translate_no():
    """ft-renderer-i18n-01: the shipped renderer must emit translate="no".

    Deliberately a weak test, and the only one here that runs without Node,
    so that a machine without Node cannot silently skip the whole dimension.
    Presence of the string is necessary, not sufficient -- the behavioural
    cases below are the real gate. Compare ft-renderer-catio-01, whose first
    version passed on a substring that also appeared in an error message.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert 'translate="no"' in src, (
        'renderer/index.html contains no translate="no" anywhere. '
        "CATDEF_SPEC.md §1392 makes this marker mandatory for content "
        'declaring .machine-translate: "Never". Value #9 makes ignoring a '
        "declared policy a conformance failure, so the reference renderer "
        "is currently non-conformant on the canonical reference file."
    )


# ---------------------------------------------------------------------------
# Behavioural cases -- the shipped renderer is executed
# ---------------------------------------------------------------------------


@requires_node
def test_extraction_finds_the_render_path():
    """ft-renderer-i18n-02: the functions under test still exist and run."""
    results = run_cases([{"name": "smoke", "value": "plain string",
                          "viewerLocale": "en", "primaryLocale": "en"}])
    assert results[0].get("error") is None, results[0]
    assert results[0]["html"] == "plain string"


@requires_node
def test_never_content_emits_translate_no():
    """ft-renderer-i18n-03 (GATING): .machine-translate "Never" -> translate="no".

    The port of ft-i18n-09 from policies/test_i18n_policies.py, driving the
    shipped renderer instead of a renderer defined in the test file.
    """
    results = run_cases([{"name": "never", "value": NEVER_TITLE,
                          "viewerLocale": "en", "primaryLocale": "en"}])
    html = results[0].get("html", "")
    assert 'translate="no"' in html, (
        'CATDEF_SPEC.md §1392: the runtime MUST mark content declaring '
        '.machine-translate: "Never" with translate="no". The shipped '
        "renderer emitted: %r" % html
    )


@requires_node
def test_allow_content_does_not_emit_translate_no():
    """ft-renderer-i18n-04 (control): permitted content is NOT suppressed.

    Marking everything translate="no" would satisfy -03 while breaking the
    authors who DID permit translation. This is the mutation that -03 alone
    cannot catch.
    """
    results = run_cases([{"name": "allow", "value": ALLOW_TITLE,
                          "viewerLocale": "en", "primaryLocale": "en"}])
    html = results[0].get("html", "")
    assert 'translate="no"' not in html, (
        "content without .machine-translate: Never must not be marked "
        "non-translatable; got %r" % html
    )


@requires_node
def test_locale_variant_is_resolved_not_serialised():
    """ft-renderer-i18n-05: a polymorphic field renders its variant, not JSON.

    Today the renderer reaches `typeof v === 'object'` in renderScalarValue
    and returns esc(JSON.stringify(v)); the card-title path reaches esc() on
    the raw object and yields the string "[object Object]".
    """
    results = run_cases([{"name": "en", "value": NEVER_TITLE,
                          "viewerLocale": "en", "primaryLocale": "en"}])
    html = results[0].get("html", "")
    assert "Field-recorded lullaby sheet music" in html, (
        "expected the .en variant; got %r" % html)
    assert "[object Object]" not in html, "raw object stringification"
    assert ".machine-translate" not in html, (
        "policy keys leaked into rendered output: %r" % html)


@requires_node
def test_rfc4647_lookup_selects_viewer_locale():
    """ft-renderer-i18n-06: RFC 4647 §3.4 Lookup, incl. progressive shortening.

    CATDEF_SPEC.md §1293. `fr-CA` has no exact variant and must shorten to
    `fr` rather than falling through to primaryLocale.
    """
    results = run_cases([
        {"name": "fr", "value": NEVER_TITLE,
         "viewerLocale": "fr", "primaryLocale": "en"},
        {"name": "fr-CA", "value": NEVER_TITLE,
         "viewerLocale": "fr-CA", "primaryLocale": "en"},
    ])
    by = {r["name"]: r.get("html", "") for r in results}
    for name in ("fr", "fr-CA"):
        html = by[name]
        assert "Partition" in html, (
            "expected the .fr variant for viewer %s; got %r" % (name, html))
        # Necessary: a serialised object contains EVERY variant, so the
        # positive assertion alone passes against JSON.stringify output.
        # Resolution means selecting one variant, not emitting all of them.
        assert "Field-recorded" not in html, (
            "viewer %s received more than one locale variant -- the value "
            "was serialised, not resolved: %r" % (name, html))


@requires_node
def test_unmatched_locale_falls_back_to_primary():
    """ft-renderer-i18n-07: no matching variant -> primaryLocale (§1293).

    primaryLocale is deliberately 'fr', NOT 'en'. With 'en' this case cannot
    distinguish the primaryLocale fallback from the last-resort "any defined
    variant" branch, because both land on the same string -- a mutation
    removing the primaryLocale lookup entirely left the suite green until
    this was changed. 'fr' sorts after 'en', so only the correct fallback
    yields the French variant.
    """
    results = run_cases([{"name": "ja", "value": NEVER_TITLE,
                          "viewerLocale": "ja", "primaryLocale": "fr"}])
    html = results[0].get("html", "")
    assert "Partition" in html, (
        "unmatched viewer locale must fall back to primaryLocale 'fr' "
        "before the last-resort branch; got %r" % html)
    assert "Field-recorded" not in html, (
        "fallback emitted more than one variant, or took the last-resort "
        "alphabetical branch instead of primaryLocale: %r" % html)


@requires_node
def test_attribute_context_helpers_honour_the_policy():
    """ft-renderer-i18n-09 (GATING): the title / alt path marks Never content.

    renderScalarValue() is not the only render path. The card title, the
    modal heading and the image alt text cannot carry markup, so they resolve
    with resolveText() and take the marker from noTranslateAttr() on the
    element. Those are the three paths that rendered "[object Object]".

    This case exists because negative controls proved the rest of this file
    could not detect a broken noTranslateAttr(): mutating it to return '',
    and mutating it to mark everything, both left the suite green. Tests
    -03/-08 cover renderScalarValue's own inline marker and nothing else.
    """
    results = run_cases([
        {"name": "never", "value": NEVER_TITLE,
         "viewerLocale": "en", "primaryLocale": "en"},
        {"name": "allow", "value": ALLOW_TITLE,
         "viewerLocale": "en", "primaryLocale": "en"},
        {"name": "plain", "value": "Carpenter's jack plane",
         "viewerLocale": "en", "primaryLocale": "en"},
    ], mode="attr")
    by = {r["name"]: r for r in results}

    assert by["never"]["attr"] == ' translate="no"', (
        "noTranslateAttr() must mark Never content for attribute-context "
        "render paths; got %r" % by["never"]["attr"])
    assert by["allow"]["attr"] == "", (
        "permitted content must not be marked non-translatable; got %r"
        % by["allow"]["attr"])
    assert by["plain"]["attr"] == "", (
        "a plain string carries no policy; got %r" % by["plain"]["attr"])

    assert by["never"]["text"] == "Field-recorded lullaby sheet music", (
        "resolveText() must yield the resolved variant as plain text, not "
        "markup and not the raw object; got %r" % by["never"]["text"])
    assert "[object Object]" not in str(by["never"]["text"])


@requires_node
def test_canonical_reference_never_fields_all_marked():
    """ft-renderer-i18n-08 (GATING): the canonical reference file renders
    conformantly.

    This is the one that makes the failure concrete. The canonical reference
    catalog is what the front-page "Try the Reference Renderer" CTA loads.
    Its Never-marked fields are a field-recorded lullaby and a soldier's
    letter to his sister, each with a human French translation and an
    explicit author declaration that they are never to be machine
    translated.
    """
    primary, never_fields = canonical_never_fields()
    assert never_fields, "fixture precondition: canonical file has Never fields"
    cases = [{"name": "%s-%d" % (k, i), "value": v,
              "viewerLocale": "en", "primaryLocale": primary}
             for i, (k, v) in enumerate(never_fields)]
    results = run_cases(cases)
    unmarked = [r["name"] for r in results
                if 'translate="no"' not in r.get("html", "")]
    assert not unmarked, (
        "%d of %d .machine-translate: Never fields in the canonical "
        "reference file render without translate=\"no\": %s"
        % (len(unmarked), len(results), ", ".join(unmarked))
    )

"""
catdef Conformance: policy-compliance gating tests (ft-i18n-07..09).

Per CLAUDE.md value #9 and CATDEF_SPEC.md §Policy Registry, policy
compliance is a first-class conformance dimension. A runtime or tool
that handles structure and content correctly but silently ignores a
declared policy is NOT conformant.

The three gating tests:

- ft-i18n-07: `.context` preservation. A tool that strips `.context`
  on export is non-conformant.
- ft-i18n-08: `.machine-translate: "Never"` — translation tooling MUST
  NOT auto-generate missing locale variants via machine translation.
- ft-i18n-09: `.machine-translate: "Never"` — runtime MUST mark
  rendered content with `translate="no"` (or platform-equivalent
  suppression mechanism for non-HTML renderers).

These tests gate catdef conformance. A runtime that fails any of them
is not conformant regardless of how well it handles other dimensions.
"""

import copy
import json
import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _load(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


REGISTERED_POLICIES = {".context", ".machine-translate"}
RESERVED_POLICIES = {".plural", ".gender", ".dir"}


def _is_policy_key(key: str) -> bool:
    return key in REGISTERED_POLICIES or key in RESERVED_POLICIES


def _is_polymorphic(value) -> bool:
    return (
        isinstance(value, dict)
        and bool(value)
        and all(isinstance(k, str) and k.startswith(".") for k in value)
    )


def _walk_polymorphic(data):
    """Yield every polymorphic-translatable-field object in data, depth-first."""
    if _is_polymorphic(data):
        yield data
    if isinstance(data, dict):
        for v in data.values():
            yield from _walk_polymorphic(v)
    elif isinstance(data, list):
        for v in data:
            yield from _walk_polymorphic(v)


# ---------------------------------------------------------------------------
# ft-i18n-07: `.context` preservation
# ---------------------------------------------------------------------------


def conformant_export(data: dict) -> dict:
    """A conformant exporter: re-serialize without stripping any members."""
    return json.loads(json.dumps(data))


def non_conformant_strip_context(data: dict) -> dict:
    """Demonstration of a NON-conformant exporter: strips `.context` entries.

    Used here only to prove that the conformance test detects such behavior.
    A real tool that behaved this way would fail ft-i18n-07.
    """
    out = copy.deepcopy(data)
    for obj in _walk_polymorphic(out):
        obj.pop(".context", None)
    return out


class TestContextPreservation:
    """ft-i18n-07: `.context` is preserved across export and passed through to
    translation tooling. A tool that strips `.context` on export is
    non-conformant.
    """

    def _count_context(self, data: dict) -> int:
        return sum(
            1 for obj in _walk_polymorphic(data) if ".context" in obj
        )

    def test_ft_i18n_07_conformant_export_preserves_context(self):
        data = _load("mt_never_content.opencatalog")
        assert self._count_context(data) > 0, "fixture precondition"
        exported = conformant_export(data)
        assert self._count_context(exported) == self._count_context(data)

    def test_ft_i18n_07_context_strip_is_detectable_as_non_conformant(self):
        """A tool that strips `.context` produces output detectable as
        non-conformant. ft-i18n-07 catches this."""
        data = _load("mt_never_content.opencatalog")
        original_count = self._count_context(data)
        stripped = non_conformant_strip_context(data)
        assert self._count_context(stripped) < original_count, (
            "non-conformant exporter should be detectable")


# ---------------------------------------------------------------------------
# ft-i18n-08: `.machine-translate: "Never"` — translator-tool enforcement
# ---------------------------------------------------------------------------


def translate_missing_locales(data: dict, target_locale: str, mt_backend) -> dict:
    """A conformant translation tool: auto-generate missing locale variants
    via `mt_backend`, but MUST skip fields with `.machine-translate: "Never"`.

    Returns a new catdef with new `.<target_locale>` entries added to
    polymorphic-translatable-field objects where permitted.
    """
    out = copy.deepcopy(data)
    for obj in _walk_polymorphic(out):
        if obj.get(".machine-translate") == "Never":
            continue  # policy: MUST NOT auto-translate
        key = f".{target_locale}"
        if key in obj:
            continue  # already present
        # Pick any available source variant.
        source_variants = [
            (k, v) for k, v in obj.items()
            if k.startswith(".") and not _is_policy_key(k) and isinstance(v, str)
        ]
        if not source_variants:
            continue
        src_key, src_value = source_variants[0]
        obj[key] = mt_backend(src_value, src_key[1:], target_locale)
    return out


def stub_mt_backend(text: str, src_locale: str, dst_locale: str) -> str:
    """Deterministic MT stub: prefixes the source text with the target locale tag."""
    return f"[{dst_locale}:{text}]"


class TestMachineTranslateToolEnforcement:
    """ft-i18n-08 (GATING): a translation tool MUST NOT auto-translate
    `.machine-translate: "Never"` content.
    """

    def _iter_translatable_objects(self, data):
        return list(_walk_polymorphic(data))

    def test_ft_i18n_08_never_fields_have_no_new_locale_added(self):
        data = _load("mt_never_content.opencatalog")
        translated = translate_missing_locales(data, "fr", stub_mt_backend)

        # For every Never-marked object: the .fr variant MUST NOT have been
        # introduced unless the writer already put it there.
        for orig_obj, new_obj in zip(
            self._iter_translatable_objects(data),
            self._iter_translatable_objects(translated),
        ):
            if orig_obj.get(".machine-translate") == "Never":
                orig_has_fr = ".fr" in orig_obj
                new_has_fr = ".fr" in new_obj
                assert orig_has_fr == new_has_fr, (
                    f"Never-marked object must not gain an auto-translated .fr variant. "
                    f"Original: {orig_obj}; after tool: {new_obj}"
                )

    def test_ft_i18n_08_allow_fields_do_get_translated(self):
        """Positive control: non-Never fields DO gain the new locale."""
        data = _load("mt_never_content.opencatalog")
        translated = translate_missing_locales(data, "fr", stub_mt_backend)
        # Find at least one polymorphic object that was NOT Never and did not
        # originally have .fr; it should now have .fr.
        added_any = False
        for orig_obj, new_obj in zip(
            self._iter_translatable_objects(data),
            self._iter_translatable_objects(translated),
        ):
            if orig_obj.get(".machine-translate") == "Never":
                continue
            if ".fr" not in orig_obj and ".fr" in new_obj:
                added_any = True
                break
        assert added_any, (
            "fixture precondition: at least one non-Never field should gain .fr")


# ---------------------------------------------------------------------------
# ft-i18n-09: `.machine-translate: "Never"` — runtime render enforcement
# ---------------------------------------------------------------------------


def _locale_variants(value):
    return {
        k[1:]: v
        for k, v in value.items()
        if k.startswith(".") and not _is_policy_key(k) and isinstance(v, str)
    }


def _resolve(value, viewer_locale: str, primary_locale):
    """Minimal resolver duplicated here for test independence."""
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return ""
    variants = _locale_variants(value)
    if not variants:
        return ""
    parts = viewer_locale.split("-")
    for i in range(len(parts), 0, -1):
        key = "-".join(parts[:i])
        if key in variants:
            return variants[key]
    if primary_locale:
        parts = primary_locale.split("-")
        for i in range(len(parts), 0, -1):
            key = "-".join(parts[:i])
            if key in variants:
                return variants[key]
    return variants[sorted(variants)[0]]


def render_to_html(value, viewer_locale: str, primary_locale) -> str:
    """Conformant HTML renderer.

    Per ft-i18n-09, content marked `.machine-translate: "Never"` MUST be
    emitted with `translate="no"` so OS-level browser translation
    (Chrome auto-translate, Safari translate-on-page) is suppressed.
    """
    resolved = _resolve(value, viewer_locale, primary_locale)
    if isinstance(value, dict) and value.get(".machine-translate") == "Never":
        return f'<span translate="no">{resolved}</span>'
    return f"<span>{resolved}</span>"


def render_non_conformant(value, viewer_locale: str, primary_locale) -> str:
    """Demonstration of a NON-conformant renderer: omits translate='no'.

    Used only to prove ft-i18n-09 detects the policy violation.
    """
    resolved = _resolve(value, viewer_locale, primary_locale)
    return f"<span>{resolved}</span>"


class TestMachineTranslateRuntimeEnforcement:
    """ft-i18n-09 (GATING): a runtime rendering `.machine-translate: "Never"`
    content MUST emit `translate="no"` on the corresponding DOM nodes.
    """

    def test_ft_i18n_09_never_content_rendered_with_translate_no(self):
        data = _load("mt_never_content.opencatalog")
        primary = data.get("primaryLocale")
        # First item's Title is Never.
        title_value = data["data"]["items"][0]["fields"]["Title"]
        html = render_to_html(title_value, "en", primary)
        assert 'translate="no"' in html, (
            "Runtime MUST emit translate=\"no\" on .machine-translate: Never content")

    def test_ft_i18n_09_allow_content_rendered_without_translate_no(self):
        """Control: non-Never content does NOT carry translate='no' (doing so
        would suppress translation for content the author DID permit)."""
        data = _load("mt_never_content.opencatalog")
        primary = data.get("primaryLocale")
        title_value = data["data"]["items"][1]["fields"]["Title"]
        assert title_value.get(".machine-translate") != "Never", "fixture precondition"
        html = render_to_html(title_value, "en", primary)
        assert 'translate="no"' not in html

    def test_ft_i18n_09_non_conformant_renderer_detectable(self):
        """A renderer that omits translate='no' on Never content is
        non-conformant; ft-i18n-09 detects this."""
        data = _load("mt_never_content.opencatalog")
        primary = data.get("primaryLocale")
        title_value = data["data"]["items"][0]["fields"]["Title"]
        html = render_non_conformant(title_value, "en", primary)
        assert 'translate="no"' not in html, "precondition: non-conformant renderer omits the marker"
        # The conformance test would flag this renderer as non-conformant.
        # We express that by asserting the conformant-renderer output differs.
        conformant_html = render_to_html(title_value, "en", primary)
        assert html != conformant_html

    def test_ft_i18n_09_never_content_plaintext_value_in_nested_field(self):
        """Provenance on item[0] is Never; its rendered output also carries translate='no'."""
        data = _load("mt_never_content.opencatalog")
        primary = data.get("primaryLocale")
        prov_value = data["data"]["items"][0]["fields"]["Provenance"]
        assert prov_value.get(".machine-translate") == "Never", "fixture precondition"
        html = render_to_html(prov_value, "en", primary)
        assert 'translate="no"' in html

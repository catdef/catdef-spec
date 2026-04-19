"""
catdef Conformance: i18n polymorphic-translatable-field tests (ft-i18n-01..06).

Per CATDEF_SPEC.md §Internationalization §Fallback semantics:

    Runtimes resolve locale variants using RFC 4647 §3.4 (Lookup) against
    the available locale variants. The catdef's primaryLocale is the
    default if no variant matches via Lookup. Last-resort fallback to
    any defined variant, with implementation-defined order, MUST emit
    a warning.

This module covers the six L1+L2 behavioral tests (ft-i18n-01..06).
Policy-compliance tests (ft-i18n-07..09) live in conformance/policies/
per value #9 (policy compliance as a first-class conformance dimension).
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


REGISTERED_POLICIES = {".context", ".machine-translate"}
RESERVED_POLICIES = {".plural", ".gender", ".dir"}


def _is_policy_key(key: str) -> bool:
    return key in REGISTERED_POLICIES or key in RESERVED_POLICIES


def _locale_variants(value: dict) -> dict[str, str]:
    """Return the locale-variant subset of a polymorphic translatable-field object.

    Strips registered/reserved policies; keeps any dot-prefixed key whose
    value is a string. BCP-47 validation is intentionally not enforced at L1.
    """
    return {
        k[1:]: v
        for k, v in value.items()
        if k.startswith(".") and not _is_policy_key(k) and isinstance(v, str)
    }


def resolve_translatable(value, viewer_locale: str, primary_locale):
    """Resolve a polymorphic translatable-field value for a given viewer locale.

    Returns (resolved_string, warnings). Implements RFC 4647 §3.4 Lookup:
    exact match, then progressively shorter match (e.g., fr-CA -> fr),
    then primaryLocale fallback, then last-resort any-defined-variant
    with a warning.

    If `value` is a plain string, it is returned unchanged.
    """
    warnings: list[str] = []

    if isinstance(value, str):
        return value, warnings

    if not isinstance(value, dict):
        warnings.append(f"unexpected translatable-field shape: {type(value).__name__}")
        return "", warnings

    variants = _locale_variants(value)
    if not variants:
        warnings.append("polymorphic translatable-field object has no locale variants")
        return "", warnings

    # RFC 4647 §3.4 Lookup: progressively shorten the viewer's tag.
    parts = viewer_locale.split("-")
    for i in range(len(parts), 0, -1):
        key = "-".join(parts[:i])
        if key in variants:
            return variants[key], warnings

    # Primary-locale fallback.
    if primary_locale:
        parts = primary_locale.split("-")
        for i in range(len(parts), 0, -1):
            key = "-".join(parts[:i])
            if key in variants:
                return variants[key], warnings

    # Last-resort: any defined variant. MUST emit a warning per the spec.
    any_key = sorted(variants)[0]
    warnings.append(
        f"locale {viewer_locale!r} not matched; primary {primary_locale!r} "
        f"also unavailable; last-resort fallback to {any_key!r}"
    )
    return variants[any_key], warnings


def resolve_label(fd: dict, viewer_locale: str, primary_locale):
    """Resolve a field_def's label through the translatable-field machinery."""
    return resolve_translatable(fd.get("label"), viewer_locale, primary_locale)


class TestL1Passthrough:
    """ft-i18n-01: L1 presented with translatable label object renders primary or skips.
    ft-i18n-02: monolingual catdef renders identically to v1.3 (no regression).
    """

    def test_ft_i18n_01_l1_renders_primary_or_skips_no_crash(self):
        data = _load("bilingual_labels.opencatalog")
        primary = data.get("primaryLocale")
        for tmpl in data.get("templates", []):
            for fd in tmpl.get("field_defs", []):
                resolved, _ = resolve_label(fd, viewer_locale=primary, primary_locale=primary)
                assert isinstance(resolved, str)

    def test_ft_i18n_02_monolingual_no_regression(self):
        data = _load("monolingual_french.opencatalog")
        for tmpl in data.get("templates", []):
            for fd in tmpl.get("field_defs", []):
                label = fd.get("label")
                resolved, warnings = resolve_translatable(label, "en", data.get("primaryLocale"))
                assert resolved == label
                assert warnings == []


class TestLocaleSelection:

    def test_ft_i18n_03_bilingual_en_viewer_sees_en(self):
        data = _load("bilingual_labels.opencatalog")
        primary = data.get("primaryLocale")
        fd = data["templates"][0]["field_defs"][0]
        resolved, warnings = resolve_label(fd, viewer_locale="en", primary_locale=primary)
        assert resolved == "Artist"
        assert warnings == []

    def test_ft_i18n_03_bilingual_fr_viewer_sees_fr(self):
        data = _load("bilingual_labels.opencatalog")
        primary = data.get("primaryLocale")
        fd = data["templates"][0]["field_defs"][0]
        resolved, warnings = resolve_label(fd, viewer_locale="fr", primary_locale=primary)
        assert resolved == "Artiste"
        assert warnings == []

    def test_ft_i18n_04_primary_locale_fallback(self):
        fd = {"label": {".fr": "Titre"}}
        resolved, warnings = resolve_translatable(
            fd["label"], viewer_locale="en", primary_locale="fr",
        )
        assert resolved == "Titre"
        assert warnings == []

    def test_ft_i18n_05_last_resort_fallback_emits_warning(self):
        data = _load("polymorphic_no_primary.opencatalog")
        primary = data.get("primaryLocale")
        fd = data["templates"][0]["field_defs"][0]
        resolved, warnings = resolve_label(fd, viewer_locale="en", primary_locale=primary)
        assert resolved == "Titre"
        assert warnings, "last-resort fallback MUST emit a warning per the spec"

    def test_ft_i18n_06_substring_fallback_fr_CA_for_fr_viewer(self):
        data = _load("locale_variants_fr_ca.opencatalog")
        primary = data.get("primaryLocale")
        fd = data["templates"][0]["field_defs"][0]

        # fr-CA viewer: exact match on .fr-CA.
        resolved, warnings = resolve_label(fd, viewer_locale="fr-CA", primary_locale=primary)
        assert resolved == "Nom"
        assert warnings == []

        # fr viewer: no .fr variant; viewer tag does not expand. Falls back
        # to primaryLocale (en) per §Fallback semantics.
        resolved, warnings = resolve_label(fd, viewer_locale="fr", primary_locale=primary)
        assert resolved == "Name"
        assert warnings == []


class TestFallbackChainEdgeCases:

    def test_plain_string_value_unchanged(self):
        resolved, warnings = resolve_translatable("Plain", "fr", "en")
        assert resolved == "Plain"
        assert warnings == []

    def test_policy_only_object_is_degenerate(self):
        value = {".context": "music", ".machine-translate": "Never"}
        resolved, warnings = resolve_translatable(value, "en", "en")
        assert resolved == ""
        assert any("locale variants" in w for w in warnings)

    def test_viewer_tag_shortens_during_lookup(self):
        """RFC 4647 Lookup: viewer fr-CA falls back to .fr when no .fr-CA present."""
        value = {".fr": "Bonjour"}
        resolved, warnings = resolve_translatable(value, "fr-CA", "en")
        assert resolved == "Bonjour"
        assert warnings == []

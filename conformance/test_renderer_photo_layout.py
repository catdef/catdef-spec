"""
catdef Conformance: a quarter-turn photo rotation must stay inside its frame
(catdef-spec#55).

Two canonical items overflow their card and clip the neighbouring title:

    RHS.2015.004  Hand-drawn Riverside town plan   rotation 90
    RHS.2022.010  Ice harvest pick                 rotation 270

The transform itself is correct. The defect is containment: both the card
hero (``.card-img img``: width/height 100% of an ``aspect-ratio:4/3`` box)
and the gallery figure (``.gallery img``: ``aspect-ratio:4/3``) lay the image
out at its PRE-rotation aspect ratio. Rotating a 4:3 box by a quarter turn
makes its visual bounding box 3:4, which is taller than the frame, so it
spills over whatever sits below.

RHS.2019.001 carries a rotation-90 photo that does not overflow visibly --
but only because it is not the item's primary photo, so it appears solely in
the gallery, where nothing sits directly beneath it to be clipped. The
gallery path emits the same unconstrained transform and has the same latent
defect; the fix therefore belongs in the shared styling function rather than
in the card layout alone.

``crop_mode`` and ``deskew`` remain deferred per CA-019 Call 4 and are not
reopened here: RHS.2022.010 declares no ``crop_mode`` at all and still
overflows, which rules them out as the cause.

SCOPE LIMIT -- read before trusting a green run. ``photoStyle()`` returns a
CSS string, so these cases prove what the renderer EMITS, not how a browser
lays it out. No box is measured. #55 was found by eye and its fix is
confirmed by eye; this file exists so the emitted contract cannot regress
silently, not to discharge the observational criterion. Per CA-021 Call 7,
automated verification does not discharge an observational criterion.
"""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER = REPO_ROOT / "renderer" / "index.html"
DRIVER = Path(__file__).parent / "renderer_photo_driver.cjs"

NODE = shutil.which("node")
requires_node = pytest.mark.skipif(
    NODE is None,
    reason="node not on PATH -- photoStyle() is NOT exercised by this run.",
)


def extract_function(src: str, name: str) -> str:
    start = src.find("\nfunction %s(" % name)
    assert start != -1, (
        "renderer/index.html no longer defines a top-level function %r; "
        "update the extraction rather than reimplementing it here." % name
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


def run_cases(cases: list) -> dict:
    src = RENDERER.read_text(encoding="utf-8")
    module_src = "\n\n".join(
        [extract_function(src, "photoStyle"), "module.exports = { photoStyle };"]
    ) + "\n"
    with tempfile.TemporaryDirectory() as td:
        mod = Path(td) / "extracted.cjs"
        mod.write_text(module_src, encoding="utf-8")
        cases_file = Path(td) / "cases.json"
        cases_file.write_text(json.dumps(cases), encoding="utf-8")
        proc = subprocess.run(
            [NODE, str(DRIVER), str(mod), str(cases_file)],
            capture_output=True, text=True, timeout=60,
        )
    assert proc.returncode == 0, "driver failed: %s" % (proc.stderr or proc.stdout)
    return {r["name"]: r for r in json.loads(proc.stdout)["results"]}


SCALE_RE = re.compile(r"scale\(\s*([0-9]*\.?[0-9]+)\s*\)")


def scale_of(style: str):
    m = SCALE_RE.search(style or "")
    return float(m.group(1)) if m else None


@requires_node
def test_no_rotation_emits_no_transform():
    """ft-renderer-photo-01: an unrotated photo is styled exactly as before."""
    r = run_cases([
        {"name": "none", "ref": {}},
        {"name": "zero", "ref": {"rotation": 0}},
    ])
    assert r["none"]["style"] == ""
    assert r["zero"]["style"] == ""


@requires_node
def test_half_turn_is_not_rescaled():
    """ft-renderer-photo-02 (control): 180° must NOT be shrunk.

    A half turn leaves the bounding box unchanged, so scaling it would shrink
    a photo that was never overflowing. This is the mutation that "scale
    everything" would otherwise slip past.
    """
    r = run_cases([{"name": "half", "ref": {"rotation": 180}}])
    style = r["half"]["style"]
    assert "rotate(180deg)" in style, style
    assert scale_of(style) is None, (
        "a half turn does not change the bounding box and must not be "
        "rescaled; got %r" % style)


@requires_node
def test_quarter_turns_are_contained():
    """ft-renderer-photo-03 (GATING): 90° and 270° must be scaled to fit.

    Both frames the renderer uses are 4:3, so a quarter-turned image needs
    scaling by 3/4 to sit inside its frame. Asserted as a bound rather than
    an exact literal: any factor that contains the rotated box is conformant,
    but 1.0 (today's behaviour) is not.
    """
    r = run_cases([
        {"name": "q90", "ref": {"rotation": 90}},
        {"name": "q270", "ref": {"rotation": 270}},
    ])
    for name, deg in (("q90", 90), ("q270", 270)):
        style = r[name]["style"]
        assert "rotate(%ddeg)" % deg in style, style
        scale = scale_of(style)
        assert scale is not None, (
            "a quarter turn overflows its 4:3 frame unless the transform "
            "also scales it; got %r" % style)
        assert 0 < scale <= 0.75 + 1e-9, (
            "scale %r does not contain a quarter-turned 4:3 image "
            "(needs <= 0.75)" % scale)


@requires_node
def test_rotation_is_normalised_before_classification():
    """ft-renderer-photo-04: -90 and 450 are quarter turns too.

    photoStyle() already normalises the angle into [0,360); the containment
    decision must be made on the normalised value, not the raw one.
    """
    r = run_cases([
        {"name": "neg90", "ref": {"rotation": -90}},
        {"name": "p450", "ref": {"rotation": 450}},
    ])
    assert "rotate(270deg)" in r["neg90"]["style"], r["neg90"]["style"]
    assert scale_of(r["neg90"]["style"]) is not None, (
        "-90 normalises to 270, a quarter turn, and must be contained")
    assert "rotate(90deg)" in r["p450"]["style"], r["p450"]["style"]
    assert scale_of(r["p450"]["style"]) is not None, (
        "450 normalises to 90, a quarter turn, and must be contained")

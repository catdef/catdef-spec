/**
 * Execution harness for the catdef reference renderer's field-rendering path.
 *
 * Like renderer_catio_driver.cjs, this file deliberately contains NO
 * rendering logic of its own. It loads functions extracted verbatim from
 * renderer/index.html and reports what they returned. Assertions live in
 * test_renderer_i18n.py.
 *
 * This matters more here than anywhere else in the suite. The file this
 * replaces -- conformance/policies/test_i18n_policies.py -- defines its own
 * `render_to_html()` and then asserts that function emits translate="no".
 * It passes green while the shipped renderer emits no such attribute,
 * because the shipped renderer is never involved. A harness that renders
 * anything itself reproduces exactly that defect (CA-021 instance 1).
 *
 * The ONE thing this harness supplies is a minimal `document.createElement`
 * shim, because the renderer's esc() escapes via a detached DOM node and
 * Node has no DOM. The shim does HTML-escaping only. It is not the behaviour
 * under test: no assertion in test_renderer_i18n.py depends on how escaping
 * is implemented, only on what the renderer does with locale variants and
 * the .machine-translate policy.
 *
 * Usage: node renderer_i18n_driver.cjs <extracted.cjs> <cases.json>
 * Writes one JSON object to stdout: { results: [ ... ] }.
 */

'use strict';

const fs = require('node:fs');
const path = require('node:path');

const [modulePath, casesPath, mode] = process.argv.slice(2);
if (!modulePath || !casesPath) {
  console.error('usage: node renderer_i18n_driver.cjs <extracted.cjs> <cases.json> [mode]');
  process.exit(2);
}

// --- minimal DOM shim, escaping only (see header) --------------------------
function escapeText(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
global.document = {
  createElement() {
    return {
      _t: '',
      set textContent(v) { this._t = escapeText(v); },
      get textContent() { return this._t; },
      get innerHTML() { return this._t; },
    };
  },
};

const mod = require(path.resolve(modulePath));
const cases = JSON.parse(fs.readFileSync(casesPath, 'utf8'));

const results = [];
for (const c of cases) {
  const out = { name: c.name };
  const opts = { viewerLocale: c.viewerLocale, primaryLocale: c.primaryLocale };
  try {
    if (mode === 'attr') {
      // The attribute-context path: card title, modal heading, image alt.
      // Markup cannot go in an attribute, so these resolve to plain text and
      // take the policy marker from noTranslateAttr() on the element.
      out.text = mod.resolveText(c.value, opts);
      out.attr = mod.noTranslateAttr(c.value);
    } else {
      // The seam under test: a field value plus the viewer's locale context.
      out.html = mod.renderScalarValue(c.value, opts);
    }
  } catch (e) {
    out.error = String((e && e.message) || e);
  }
  results.push(out);
}

process.stdout.write(JSON.stringify({ results }));

/**
 * Execution harness for the catdef reference renderer's typed-field dispatch.
 *
 * Contains NO formatting logic of its own. It loads renderTypedValue()
 * extracted verbatim from renderer/index.html and reports what it returned.
 * Assertions live in test_renderer_field_types.py.
 *
 * `null` is a meaningful result, not an error: it means "this type is not
 * mine", and the renderer's existing generic path handles the value. Several
 * cases assert exactly that, so the harness must distinguish null from
 * undefined and from a thrown error rather than collapsing them.
 *
 * The DOM shim is escaping only, as in renderer_i18n_driver.cjs, because
 * esc() escapes via a detached node and Node has no DOM. No assertion
 * depends on how escaping is implemented.
 *
 * Usage: node renderer_field_types_driver.cjs <extracted.cjs> <cases.json>
 */

'use strict';

const fs = require('node:fs');
const path = require('node:path');

const [modulePath, casesPath] = process.argv.slice(2);
if (!modulePath || !casesPath) {
  console.error('usage: node renderer_field_types_driver.cjs <extracted.cjs> <cases.json>');
  process.exit(2);
}

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
  try {
    const v = mod.renderTypedValue(c.value, c.fd, {});
    // Normalise undefined to null so "not mine" is one value in the report.
    out.html = (v === undefined) ? null : v;
  } catch (e) {
    out.error = String((e && e.message) || e);
    out.html = null;
  }
  results.push(out);
}

process.stdout.write(JSON.stringify({ results }));

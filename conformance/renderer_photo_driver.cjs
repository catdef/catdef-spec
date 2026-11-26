/**
 * Execution harness for the catdef reference renderer's photo-layout styling.
 *
 * As with the other renderer drivers, this file contains NO styling logic of
 * its own. It loads photoStyle() extracted verbatim from renderer/index.html
 * and reports what it returned. Assertions live in
 * test_renderer_photo_layout.py.
 *
 * Scope limit, stated here because it is easy to over-read: photoStyle() is
 * a pure string-producing function, so this harness proves what CSS the
 * renderer EMITS. It cannot prove how a browser LAYS THAT OUT -- no box is
 * measured here. catdef-spec#55 was found by eye and its fix is confirmed by
 * eye; these cases exist so that a regression in the emitted contract is
 * caught mechanically, not so that the visual criterion is discharged.
 *
 * Usage: node renderer_photo_driver.cjs <extracted.cjs> <cases.json>
 * Writes one JSON object to stdout: { results: [ ... ] }.
 */

'use strict';

const fs = require('node:fs');
const path = require('node:path');

const [modulePath, casesPath] = process.argv.slice(2);
if (!modulePath || !casesPath) {
  console.error('usage: node renderer_photo_driver.cjs <extracted.cjs> <cases.json>');
  process.exit(2);
}

const mod = require(path.resolve(modulePath));
const cases = JSON.parse(fs.readFileSync(casesPath, 'utf8'));

const results = [];
for (const c of cases) {
  const out = { name: c.name };
  try {
    out.style = mod.photoStyle(c.ref);
  } catch (e) {
    out.error = String((e && e.message) || e);
  }
  results.push(out);
}

process.stdout.write(JSON.stringify({ results }));

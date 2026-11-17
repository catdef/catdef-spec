/**
 * Execution harness for the catdef reference renderer's CATIO loader.
 *
 * This file deliberately contains NO import logic of its own. It loads the
 * block extracted verbatim from renderer/index.html and reports what that
 * code did. Assertions live in test_renderer_catio.py, so this harness can
 * never accidentally become a second implementation that passes while the
 * shipped renderer fails — the failure mode that let CA-017 sit for 158 days
 * behind a green suite.
 *
 * Usage: node renderer_catio_driver.cjs <extracted-loader.cjs> <manifest.json>
 * Writes one JSON object to stdout: { results: [ ... ] }.
 */

'use strict';

const fs = require('node:fs');
const crypto = require('node:crypto');

const [loaderPath, manifestPath] = process.argv.slice(2);
if (!loaderPath || !manifestPath) {
  console.error('usage: node renderer_catio_driver.cjs <loader.cjs> <manifest.json>');
  process.exit(2);
}

const loader = require(require('node:path').resolve(loaderPath));
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

function sha256(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}

(async () => {
  const results = [];

  for (const testCase of manifest.cases) {
    const record = { name: testCase.name };
    try {
      const bytes = new Uint8Array(fs.readFileSync(testCase.path));
      record.sniffed_zip = loader.catioIsZip(bytes);

      const out = await loader.catioRead(bytes);

      record.ok = true;
      record.document_name = out.documentName;
      record.media_names = Array.from(out.media.keys()).sort();
      record.media_sha256 = {};
      for (const [name, value] of out.media) {
        record.media_sha256[name] = sha256(value);
        // Guard against a loader that returns a string or a view with the
        // wrong byte offsets: record what we actually got.
        record.media_sha256[name + '::len'] = value.length;
      }
      const json = out.json;
      record.json_top_keys = Object.keys(json).sort();
      record.catdef_version = json.catdef || null;
      record.catio_version = json.catio || null;
      record.item_count =
        json.data && Array.isArray(json.data.items) ? json.data.items.length : null;
      // Photo filenames the document references, so the test can check that
      // every reference resolves against the unpacked media map.
      const refs = [];
      if (json.data && Array.isArray(json.data.items)) {
        for (const item of json.data.items) {
          const fields = (item && item.fields) || {};
          for (const key of Object.keys(fields)) {
            if (key.toLowerCase() !== 'photos' && key.toLowerCase() !== 'photo') continue;
            const value = fields[key];
            const list = Array.isArray(value) ? value : [value];
            for (const ref of list) {
              if (ref && typeof ref === 'object' && ref.filename) refs.push(ref.filename);
              else if (typeof ref === 'string') refs.push(ref);
            }
          }
        }
      }
      record.photo_refs = Array.from(new Set(refs)).sort();
      record.unresolved_refs = record.photo_refs
        .filter(name => !out.media.has(name))
        .sort();
    } catch (err) {
      record.ok = false;
      record.error = err && err.message ? err.message : String(err);
    }
    results.push(record);
  }

  process.stdout.write(JSON.stringify({ results }, null, 2));
})().catch(err => {
  console.error('driver failure:', err && err.stack ? err.stack : err);
  process.exit(3);
});

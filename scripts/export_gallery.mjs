#!/usr/bin/env node
// Canonical, deterministic producer for the site's evidence-backed registry tile.
// It deliberately represents inventory size, not architecture, maturity or quality.
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const input = join(root, 'registry/registry.json');
const output = join(root, 'gallery/preview.v1.json');

export function buildPreview(source) {
  const raw = Buffer.isBuffer(source) ? source : Buffer.from(source, 'utf8');
  const registry = JSON.parse(raw.toString('utf8'));
  const fields = ['systems', 'triggers', 'recommendations'];
  for (const field of fields) {
    if (!Array.isArray(registry[field])) throw new Error('Missing registry array: ' + field);
  }
  if (registry.triggers.some(t => typeof t.family !== 'string' || !t.family)) {
    throw new Error('Every trigger must have a nonempty problem family');
  }
  const ids = (xs) => new Set(xs.map(x => x.id));
  const systems = ids(registry.systems), triggers = ids(registry.triggers);
  if (systems.size !== registry.systems.length || triggers.size !== registry.triggers.length) {
    throw new Error('Duplicate system or trigger identifiers');
  }
  if (registry.recommendations.some(r => !systems.has(r.system_id) || !triggers.has(r.trigger_id))) {
    throw new Error('Recommendation refers to an absent system or trigger');
  }
  const source_git_blob_sha = createHash('sha1')
    .update(Buffer.from('blob ' + raw.length + '\0')).update(raw).digest('hex');
  return {
    schema_version: 1,
    project_id: 'cavebot-collective/right-tool',
    visual: {
      kind: 'registry_inventory',
      title: 'Registry inventory',
      description: 'Source registry entries; counts do not establish completeness, performance, or architectural structure.',
      metrics: [
        { id: 'systems', label: 'Systems', value: registry.systems.length },
        { id: 'triggers', label: 'Triggers', value: registry.triggers.length },
        { id: 'recommendations', label: 'Recommendations', value: registry.recommendations.length },
        { id: 'families', label: 'Problem families', value: new Set(registry.triggers.map(t => t.family)).size }
      ]
    },
    evidence: {
      status: 'observed',
      source_path: 'registry/registry.json',
      source_git_blob_sha,
      derived_by: 'scripts/export_gallery.mjs'
    }
  };
}

const isMain = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const rendered = JSON.stringify(buildPreview(readFileSync(input)), null, 2) + '\n';
  if (process.argv.includes('--check')) {
    if (readFileSync(output, 'utf8') !== rendered) {
      throw new Error('Gallery preview stale: run node scripts/export_gallery.mjs');
    }
    console.log('Gallery preview matches registry source');
  } else {
    writeFileSync(output, rendered, 'utf8');
    console.log('Generated gallery/preview.v1.json');
  }
}

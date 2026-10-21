import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildPreview } from '../scripts/export_gallery.mjs';

const raw = readFileSync('registry/registry.json');
const manifest = JSON.parse(readFileSync('gallery/preview.v1.json', 'utf8'));

test('produced visual is exactly reproducible from the registry bytes', () => {
  assert.deepEqual(buildPreview(raw), manifest);
});

test('metric values have explicit, source-backed semantics', () => {
  const registry = JSON.parse(raw);
  const byId = Object.fromEntries(manifest.visual.metrics.map(m => [m.id,m.value]));
  assert.deepEqual(byId, {
    systems: registry.systems.length,
    triggers: registry.triggers.length,
    recommendations: registry.recommendations.length,
    families: new Set(registry.triggers.map(t => t.family)).size
  });
  assert.equal(manifest.visual.kind, 'registry_inventory');
  assert.equal(manifest.evidence.status, 'observed');
  assert.match(manifest.evidence.source_git_blob_sha, /^[a-f0-9]{40}$/);
});

test('no fabricated stages, directed edges or inferred topology', () => {
  const preview = JSON.stringify(manifest);
  assert.ok(!('steps' in manifest.visual));
  for(const bad of ['nodes','edges','links','layout','flow','architecture','performance_score']) {
    assert.equal(Object.hasOwn(manifest.visual,bad),false,bad);
  }
});

test('producer rejects dangling relation endpoints', () => {
  const clone = JSON.parse(raw);
  clone.recommendations[0].system_id = 'does-not-exist';
  assert.throws(() => buildPreview(JSON.stringify(clone)), /absent system or trigger/);
});

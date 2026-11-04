const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const { mkdtemp, mkdir, writeFile, rm } = require('node:fs/promises');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const lock = require('../../package-lock.json');
const legacy = require('minimatch');
const modern = createRequire(require.resolve('minimatch'))('minimatch-modern');

test('deepmerge cannot poison returned prototypes through either input', () => {
  const merge = require('deepmerge');
  const malicious = () => JSON.parse('{"__proto__":{"injected":true},"safe":1}');
  for (const options of [{}, { clone: false }, { isMergeableObject: value => value !== null && typeof value === 'object' }]) {
    for (const [target, source] of [
      [malicious(), {}],
      [{}, malicious()],
      [Object.create(null), malicious()],
      [malicious(), malicious()],
    ]) {
      const result = merge(target, source, options);
      assert.equal(Object.getPrototypeOf(result), Object.prototype);
      assert.equal(result.injected, undefined);
      assert.equal(Object.hasOwn(result, '__proto__'), false);
      assert.equal(result.safe, 1);
    }
  }
  const nested = merge({}, { nested: malicious(), list: [malicious()] });
  assert.equal(nested.nested.injected, undefined);
  assert.equal(nested.list[0].injected, undefined);
  assert.equal({}.injected, undefined);
});

test('deepmerge retains merge options and all consumers resolve the patch', () => {
  const merge = require('deepmerge');
  const symbol = Symbol('metadata');
  const target = { nested: { a: 1 }, list: [1], [symbol]: { a: 1 } };
  const source = { nested: { b: 2 }, list: [2], [symbol]: { b: 2 } };
  assert.deepEqual(merge(target, source), {
    nested: { a: 1, b: 2 }, list: [1, 2], [symbol]: { a: 1, b: 2 },
  });
  assert.deepEqual(merge(target, source, { arrayMerge: (_, incoming) => incoming }).list, [2]);
  assert.equal(merge({ value: 2 }, { value: 3 }, { customMerge: key => key === 'value' ? (a, b) => a + b : undefined, isMergeableObject: () => true }).value, 5);
  assert.deepEqual(merge.all([{ a: 1 }, { b: 2 }]), { a: 1, b: 2 });
  assert.equal(require('deepmerge/package.json').name, '@devplaninc/deepmerge');
  for (const consumer of ['jest-config', '@rollup/plugin-node-resolve']) {
    assert.equal(createRequire(require.resolve(consumer))('deepmerge'), merge);
  }
  for (const [path, entry] of Object.entries(lock.packages)) {
    if (path.endsWith('/deepmerge')) {
      assert.equal(entry.resolved, 'file:vendor/deepmerge');
      assert.equal(entry.name, '@devplaninc/deepmerge');
    }
  }
});

test('minimatch bounds globparts amplification and large-set deduplication', () => {
  const { Minimatch } = require('minimatch');
  const pattern = Array(30).fill('**/../a/b').join('/');
  const bounded = new Minimatch(pattern, { optimizationLevel: 2, braceExpandMax: 64 });
  assert.ok(bounded.globParts.length <= 64);
  const large = new Minimatch('{x,*}/{0..999}', { optimizationLevel: 2 });
  assert.equal(large.match('x/5'), true);
  assert.equal(large.match('y/999'), true);
  assert.equal(large.match('.y/5'), false);
});

test('legacy callable exports use the patched minimatch implementation', () => {
  assert.equal(legacy, modern.minimatch);
  assert.equal(createRequire(require.resolve('eslint'))('minimatch'), legacy);
  assert.equal(createRequire(require.resolve('@eslint/config-array'))('minimatch'), legacy);
  assert.equal(createRequire(require.resolve('@eslint/eslintrc'))('minimatch'), legacy);
  assert.equal(legacy('src/app/page.tsx', 'src/**/*.{ts,tsx}'), true);
  assert.equal(legacy('src/app/page.js', 'src/**/*.{ts,tsx}'), false);
  assert.equal(legacy('.hidden.ts', '*.ts'), false);
  assert.equal(legacy.defaults({ dot: true })('.hidden.ts', '*.ts'), true);
  assert.equal(legacy('src/APP.ts', '*.ts', { matchBase: true }), true);
  assert.deepEqual(['src/a.ts', 'src/b.js'].filter(legacy.filter('**/*.ts')), ['src/a.ts']);
  assert.deepEqual(legacy.match(['src/a.ts', 'src/b.js'], '**/*.ts'), ['src/a.ts']);
  assert.equal(new legacy.Minimatch('src/**').match('src/index.ts'), true);
  const matcher = new legacy.Minimatch(Array(30).fill('**/../a/b').join('/'), { optimizationLevel: 2, braceExpandMax: 64 });
  assert.ok(matcher.globParts.length <= 64);
  const semver = require('semver');
  for (const [path, entry] of Object.entries(lock.packages)) {
    if (path.endsWith('/minimatch')) {
      if (entry.name === '@devplaninc/minimatch-compat') {
        assert.equal(entry.resolved, 'file:vendor/minimatch-compat');
      } else {
        assert.ok(semver.gte(entry.version, '11.0.1'), path);
      }
    }
    if (entry.name === 'minimatch') assert.ok(semver.gte(entry.version, '11.0.1'), path);
    if (path.endsWith('/glob')) assert.ok(semver.gte(entry.version, '14.0.2'), path);
  }
});

test('ESLint still selects files and applies configured rules', async () => {
  const { ESLint } = require('eslint');
  const eslint = new ESLint({
    overrideConfigFile: true,
    overrideConfig: [{ files: ['**/*.js'], rules: { 'no-undef': 'error' } }],
  });
  const results = await eslint.lintText('missing();', { filePath: 'src/security-fixture.js' });
  assert.equal(results[0].messages[0].ruleId, 'no-undef');
});

test('test-exclude discovers source files and excludes tests with glob 14', async () => {
  const TestExclude = require('test-exclude');
  const directory = await mkdtemp(join(tmpdir(), 'coverage-security-'));
  try {
    await mkdir(join(directory, 'src'));
    await writeFile(join(directory, 'src/index.ts'), 'export const value = 1;');
    await writeFile(join(directory, 'src/index.test.ts'), '');
    const exclude = new TestExclude({ cwd: directory, extension: ['.ts'], include: ['src/**'], exclude: ['**/*.test.ts'] });
    assert.deepEqual(exclude.globSync(), ['src/index.ts']);
    assert.deepEqual(await exclude.glob(), ['src/index.ts']);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test('minimatch supports ESM named imports alongside callable CommonJS', async () => {
  const imported = await import('minimatch');
  assert.equal(imported.default, legacy);
  assert.equal(imported.minimatch, legacy);
  assert.equal(imported.Minimatch, modern.Minimatch);
});


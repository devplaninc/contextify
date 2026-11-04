# Minimatch export compatibility

This adapter exposes patched upstream minimatch 11 as a callable CommonJS
export and named exports. Older ESLint consumers call the module directly;
modern glob and TypeScript tooling use its named exports. All matching delegates
to the npm alias `minimatch-modern`; no legacy matching implementation is kept.

Jest and Rollup tooling are upgraded to remove glob 7/8, which depend on old
minimatch internals. This adapter does not implement removed APIs such as
`makeRe`. Tests cover callable/ESM exports, ESLint selection, coverage discovery,
and bounded globparts expansion. Remove the adapter once all consumers adopt
the modern export shape.

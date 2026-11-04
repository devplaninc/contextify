# Temporary deepmerge security patch

This is the MIT-licensed CommonJS distribution and TypeScript declarations from
`deepmerge@4.3.1`, with the same prototype-key guards reviewed in devplaninc/webapp
PR #1231. The root dependency and override route all consumers to this private
package. The web Docker build copies `web/vendor` before dependency installation.

[GHSA-gcqx-w48m-w2h4](https://github.com/advisories/GHSA-gcqx-w48m-w2h4)
has no patched upstream release. Both the target-copy and source-merge loops skip
`__proto__`, including null-prototype targets and own enumerable `__proto__`
properties. This prevents assignment through the inherited prototype setter.
Other merging behavior and the bundled object-type predicate remain unchanged.

Run `npm run test:dependency-security` from `web` for exploit regressions and
consumer-resolution checks. Jest tests and Rollup builds exercise the actual
consumers. Replace this local package with a reviewed upstream fix when available,
retaining the regression tests. Its private package name is not evidence of a fix;
the source guards and tests establish the mitigation.

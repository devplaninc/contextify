# Contextify Dependabot alerts 314–321

Reviewed and remediated November 3, 2026. Alert links are under
https://github.com/devplaninc/contextify/security/dependabot.

| Alerts | Package | Remediation |
| --- | --- | --- |
| #314 | langgraph | Upgrade 1.2.6 to 1.2.19 and require >=1.2.14. Require langgraph-sdk >=0.4.6; the lock already had SDK 0.4.6. |
| #315–#318 | pyasn1 | Upgrade 0.6.4 to 0.6.5 and raise the manifest floor to cover all four decoding CPU advisories. |
| #319 | deepmerge | No patched upstream release exists. Route all consumers to the local 4.3.1 patch that rejects `__proto__` in both object-copy paths. |
| #320 | follow-redirects | Upgrade 1.16.1 to 1.16.2 and raise the override floor. |
| #321 | minimatch | Use patched upstream 11.0.4 through an export adapter for old callable CommonJS consumers and modern named imports. No old matching implementation remains. |

The Python floors also protect builds that install from `pyproject.toml` instead
of the lockfile. Only langgraph and pyasn1 change versions in `server/uv.lock`.

Jest 30, its compatible types/transformer, and Rollup's CommonJS plugin 29 remove
old glob consumers that depend on minimatch internals. Glob is constrained to
>=14.0.2 (locked at 14.0.3) to avoid its cancellation advisory, and test-exclude
is upgraded to 8 for coverage discovery compatibility. The minimatch adapter
does not implement removed APIs such as `makeRe`.

The npm lockfile was regenerated to apply overrides consistently. It also
refreshes other dependencies within existing manifest ranges, including React,
Clerk, cloud SDKs, and build tooling. This is a broader lockfile refresh than the
Python update. The existing frontend and API builds and tests passed against
the resulting tree.

The local [deepmerge patch](../../web/vendor/deepmerge/README.md) retains the
upstream MIT license and changes only the two prototype-key guards. Regression
tests cover both inputs, null-prototype targets, nested values, merge options,
and resolution by Jest and Rollup. Its private package name alone does not
establish remediation; these guards and tests do. Replace it with a reviewed
upstream fix when one becomes available.

`web/.npmrc` uses packed local dependencies (`install-links=true`), and the web
Dockerfile copies it and `web/vendor` before installing dependencies. The new
security tests run through `make test` in existing CI.

Validation:

- 156 Python tests passed with Repomix available, plus BER container, string,
  BIT STRING, and REAL round-trip smoke checks.
- 42 API tests passed under Jest 30.
- Seven dependency security tests passed, including bounded minimatch expansion,
  callable/ESM exports, ESLint selection, and coverage file discovery.
- API browser/Node bundles and declarations, and the frontend production build,
  passed. Rollup emitted dependency annotation and bundle-size warnings.
- Clean `npm ci`, `uv sync --locked`, `uv lock --check`, and `git diff --check`
  passed; npm audit reported zero vulnerabilities.

These changes require merging and normal deployment. No Dependabot alerts were
manually dismissed, and no production runtime validation was performed.

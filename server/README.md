## Setup

Create file [.env.local.secrets](.env.local.secrets) and add following there:
```
DEV_OBSERVER__GIT__GITHUB__PERSONAL_TOKEN=<Github personal token, use `gh auth token` to get>
DEV_OBSERVER__GIT__GITHUB__PRIVATE_KEY=<GH private key if app auth is used>
DEV_OBSERVER__GIT__GITHUB__APP_ID="<GH APP ID if app auth is used>"
GOOGLE_API_KEY=<GOOGLE_API_TOKEN to use for google-genai>
DEV_OBSERVER__USERS_MANAGEMENT__CLERK__SECRET_KEY=<get key from Clerk>
```

## Testing

```bash
uv run scripts/self_analysis/main.py
```

## Automatic Forge token retention

PostgreSQL-backed Jira/Confluence system token groups retain the three newest
expired records (ordered by creation time, then ID), all currently valid records,
and all records without an expiry. Extra expired records are eligible immediately;
a group must have a currently valid replacement before anything is pruned.
The policy covers provider `JIRA`, the default namespace, a nonempty workspace
(including `confluence:` workspaces), and no repository scope. Null and empty
repository scopes are treated alike. Personal tokens and other scopes are excluded.

Managed writes serialize per group across processes and apply retention in the
same transaction. Repeated submissions of the same credential and expiry reuse
its record; stale `instead_of_id` hints cannot remove another group's credential.
A just-submitted expired credential remains available in the write response, even
if it is an older replay beyond the three backups; the next sweep removes that
temporary exception. Encryption and replay checks run on worker threads. No schema
migration is needed.

The existing background processor also sweeps on its first polling tick and then
at most once per 15 minutes per process, including after failures. Each sweep
visits at most 100 eligible groups, deletes at most 500 rows per group, skips groups
being refreshed, and has a 10-second total time budget. Normal background polling
continues after failures. Successful deletions log a count; credentials are not
logged. Large backlogs converge across subsequent sweeps or refreshes.

Deployment is required to enable this behavior. The first sweep can prune existing
history under this policy; database backup/PITR is the recovery path for deleted
records. Groups without a valid replacement and unknown-expiry records can still
accumulate intentionally and need separate investigation.

Run the PostgreSQL regression tests against a disposable local database:

```bash
TEST_POSTGRES_URL=postgresql+asyncpg://postgres:password@localhost:5432/contextify_test \
  PYTHONPATH=src uv run pytest tests/dev_observer/test_forge_token_retention.py \
  tests/dev_observer/test_token_decryption.py
```

The tests create isolated schemas and remove them afterward. CI provides a
PostgreSQL service and runs these tests as part of `make test`.

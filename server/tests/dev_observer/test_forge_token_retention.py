"""Integration tests use real PostgreSQL, encrypted rows, and concurrent sessions."""
import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import insert, select, text
from starlette.requests import Request

from dev_observer.api.types.tokens_pb2 import AuthToken, AuthTokenProvider
from dev_observer.common.crypto import Encryptor
from dev_observer.processors.periodic import PeriodicProcessor
from dev_observer.processors.token_retention import TokenRetentionMaintenance
from dev_observer.server.services.tokens import TokensService
from dev_observer.storage.postgresql.model import AuthTokenEntity, Base, GlobalConfigEntity
from dev_observer.storage.postgresql.provider import PostgresqlStorageProvider


@asynccontextmanager
async def database():
    url = os.environ.get("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Set TEST_POSTGRES_URL to run against a real test PostgreSQL database")
    schema = f"forge_retention_{uuid4().hex}"
    encryptor = Encryptor("test-only-forge-secret")
    stores = [PostgresqlStorageProvider(url, encryptor) for _ in range(2)]
    for store in stores:
        store._engine.update_execution_options(schema_translate_map={None: schema})
    engine = stores[0]._engine
    try:
        async with engine.begin() as conn:
            await conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(insert(GlobalConfigEntity), {"id": "global_config", "json_data": "{}"})
        yield stores, encryptor
    finally:
        async with engine.begin() as conn:
            await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        await asyncio.gather(*(store._engine.dispose() for store in stores))


def token(value="new-token", workspace="jira-site", expiry=None, **kwargs):
    result = AuthToken(provider=AuthTokenProvider.JIRA, system=True, workspace=workspace, token=value, **kwargs)
    if expiry is not None:
        result.expires_at.FromDatetime(expiry)
    return result


async def seed(store, encryptor, name, *, workspace="jira-site", age=10, expires=-3,
               system=True, provider=AuthTokenProvider.JIRA, namespace="", repo=""):
    now = datetime.now(timezone.utc)
    token_id = str(uuid4())
    values = dict(id=token_id, namespace=namespace, provider=provider, workspace=workspace,
                  repo=repo, system=system, token=encryptor.encrypt(name, token_id),
                  expires_at=None if expires is None else now + timedelta(days=expires),
                  created_at=now - timedelta(days=age), updated_at=now)
    async with store._engine.begin() as conn:
        await conn.execute(insert(AuthTokenEntity), values)
    return token_id


async def ids(store):
    async with store._engine.connect() as conn:
        return set((await conn.scalars(select(AuthTokenEntity.id))).all())


def test_concurrent_replays_ignore_stale_and_foreign_replacement_hints():
    async def run():
        async with database() as (stores, encryptor):
            old = await seed(stores[0], encryptor, "old", repo=None)
            foreign = await seed(stores[0], encryptor, "personal", system=False)
            expiry = datetime.now(timezone.utc) + timedelta(hours=1)
            request = token(expiry=expiry)
            results = await asyncio.gather(*(
                stores[i % 2].add_token(request, old if i % 2 else foreign)
                for i in range(8)
            ))
            assert len({result.id for result in results}) == 1
            assert all(result.token == "new-token" for result in results)
            assert await ids(stores[0]) == {old, foreign, results[0].id}
            # A distinct live credential must not replace the earlier valid one.
            distinct = await asyncio.gather(*(
                stores[i % 2].add_token(token(f"distinct-{i}", expiry=expiry), old)
                for i in range(4)
            ))
            assert {r.id for r in results + distinct}.issubset(await ids(stores[0]))
    asyncio.run(run())


@pytest.mark.parametrize("trigger", ["write", "sweep"])
def test_retention_preserves_protected_rows_and_scopes(trigger):
    async def run():
        async with database() as (stores, encryptor):
            store = stores[0]
            protected = set()
            # Retain three expired backups separately from valid and undated rows.
            for age in (1, 2, 3):
                protected.add(await seed(store, encryptor, f"recent-{age}", age=age, expires=-2))
            protected.add(await seed(store, encryptor, "valid", age=10, expires=1))
            protected.add(await seed(store, encryptor, "undated", age=10, expires=None))
            deletable = {await seed(store, encryptor, "obsolete", age=12, repo=None),
                         await seed(store, encryptor, "obsolete-empty", age=13),
                         await seed(store, encryptor, "recently-expired", age=10, expires=-0.1)}
            for params in [dict(system=False), dict(provider=AuthTokenProvider.BIT_BUCKET),
                           dict(namespace="other"), dict(repo="repo/name"), dict(workspace="")]:
                protected.add(await seed(store, encryptor, "outside-policy", age=20, **params))
            for i in range(5):
                protected.add(await seed(store, encryptor, "no-valid", workspace="no-valid", age=i+10))
            if trigger == "write":
                added = await store.add_token(token("another-valid", expiry=datetime.now(timezone.utc)+timedelta(days=1)))
                protected.add(added.id)
            else:
                assert await store.cleanup_expired_forge_tokens() == 3
            assert await ids(store) == protected
            assert await stores[1].cleanup_expired_forge_tokens() == 0
    asyncio.run(run())


def test_no_valid_replacement_prevents_cleanup_and_unknown_expiry_survives_service():
    async def run():
        async with database() as (stores, encryptor):
            store = stores[0]
            for i in range(5):
                await seed(store, encryptor, f"expired-{i}", age=i+2)
            original = await ids(store)
            await store.add_token(token("expired-input", expiry=datetime.now(timezone.utc)-timedelta(days=2)))
            assert original.issubset(await ids(store))
            assert await store.cleanup_expired_forge_tokens() == 0
            # Exercise protobuf field presence through the real HTTP handler.
            body = json.dumps({"token": {"provider": "JIRA", "system": True,
                                          "workspace": "jira-site", "token": "unknown-expiry"}}).encode()
            incoming = asyncio.Queue()
            incoming.put_nowait({"type": "http.request", "body": body, "more_body": False})
            response = await TokensService(store).add_token(Request({"type": "http"}, incoming.get))
            saved = await store.get_token(response["token"]["id"])
            assert not saved.HasField("expires_at")
    asyncio.run(run())


def test_write_failure_rolls_back_insertion_and_pruning():
    async def run():
        async with database() as (stores, encryptor):
            store = stores[0]
            for i in range(5):
                await seed(store, encryptor, f"old-{i}", age=i+5)
            original = await ids(store)
            # A real DB constraint rejects the new row; no partial deletion may commit.
            request = token("different", expiry=datetime.now(timezone.utc)+timedelta(hours=1), id=next(iter(original)))
            from sqlalchemy.exc import IntegrityError
            with pytest.raises(IntegrityError):
                await store.add_token(request)
            assert await ids(store) == original
    asyncio.run(run())


def test_sweeper_cadence_failure_recovery_and_periodic_wiring(caplog):
    async def run():
        async with database() as (stores, encryptor):
            store = stores[0]
            maintenance = TokenRetentionMaintenance(store, interval_seconds=0.1)
            async with store._engine.begin() as conn:
                await conn.run_sync(AuthTokenEntity.__table__.drop)
            await maintenance.run_if_due()  # Actual SQL failure is contained.
            assert "retention sweep failed" in caplog.text
            async with store._engine.begin() as conn:
                await conn.run_sync(AuthTokenEntity.__table__.create)
            for i in range(5):
                await seed(store, encryptor, f"old-{i}", age=i+5)
            await seed(store, encryptor, "valid", age=2, expires=1)
            await asyncio.sleep(0.11)
            await maintenance.run_if_due()
            assert len(await ids(store)) == 4
            # Default cadence suppresses a second sweep without sleeping 15 minutes.
            default = TokenRetentionMaintenance(store)
            await default.run_if_due()
            await seed(store, encryptor, "new-old", age=20)
            await default.run_if_due()
            assert len(await ids(store)) == 5
            # Actual PeriodicProcessor.run wiring prunes it on its startup tick.
            # No processing items exist, so unrelated analysis collaborators are unused.
            processor = PeriodicProcessor(store, None, None, None)
            task = asyncio.create_task(processor.run())
            try:
                async with asyncio.timeout(5):
                    while len(await ids(store)) != 4:
                        await asyncio.sleep(0.1)
            finally:
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
    asyncio.run(run())


def test_sweep_and_refresh_share_group_lock_for_confluence():
    async def run():
        from dev_observer.storage.postgresql.provider import _forge_lock_key
        async with database() as (stores, encryptor):
            workspace = "confluence:another-site"
            for i in range(5):
                await seed(stores[0], encryptor, f"old-{i}", workspace=workspace, age=i+5)
            current = await seed(stores[0], encryptor, "current", workspace=workspace, expires=1)
            async with stores[0]._engine.begin() as conn:
                await conn.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": _forge_lock_key(workspace)})
                refresh = asyncio.create_task(stores[1].add_token(token(
                    "refreshed", workspace=workspace, expiry=datetime.now(timezone.utc)+timedelta(hours=1),
                ), current))
                try:
                    # Sweep sees excess history, but skips a group held by another transaction.
                    assert await stores[0].cleanup_expired_forge_tokens() == 0
                    assert len(await ids(stores[0])) == 6
                except BaseException:
                    refresh.cancel()
                    raise
            added = await refresh
            assert len(await ids(stores[0])) == 5  # Three expired and two valid.
            assert {current, added.id}.issubset(await ids(stores[0]))
            assert await stores[0].cleanup_expired_forge_tokens() == 0
    asyncio.run(run())


def test_periodic_polling_continues_after_cleanup_sql_failure(caplog):
    async def run():
        from sqlalchemy import event
        async with database() as (stores, encryptor):
            store = stores[0]
            async with store._engine.begin() as conn:
                await conn.run_sync(AuthTokenEntity.__table__.drop)
            config_polled = asyncio.Event()

            def observe_statement(conn, cursor, statement, parameters, context, executemany):
                if statement.startswith("SELECT") and "global_config" in statement:
                    config_polled.set()

            event.listen(store._engine.sync_engine, "after_cursor_execute", observe_statement)
            processor = PeriodicProcessor(store, None, None, None)
            task = asyncio.create_task(processor.run())
            try:
                async with asyncio.timeout(5):
                    await config_polled.wait()
                assert "retention sweep failed" in caplog.text
                assert not task.done()
            finally:
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
                event.remove(store._engine.sync_engine, "after_cursor_execute", observe_statement)
    asyncio.run(run())


def test_expired_replay_is_returned_then_converges_on_next_sweep():
    async def run():
        async with database() as (stores, encryptor):
            store = stores[0]
            for i in range(4):
                await seed(store, encryptor, f"expired-{i}", age=i+5)
            await seed(store, encryptor, "valid", expires=1)
            async with store._engine.connect() as conn:
                oldest = (await conn.execute(select(AuthTokenEntity.id, AuthTokenEntity.expires_at)
                    .where(AuthTokenEntity.expires_at < datetime.now(timezone.utc))
                    .order_by(AuthTokenEntity.created_at).limit(1))).one()
            replayed = await store.add_token(token("expired-3", expiry=oldest.expires_at))
            assert replayed.id == oldest.id
            assert await store.get_token(replayed.id) is not None
            assert len(await ids(store)) == 5
            assert await store.cleanup_expired_forge_tokens() == 1
            assert replayed.id not in await ids(store)
            assert len(await ids(store)) == 4
    asyncio.run(run())

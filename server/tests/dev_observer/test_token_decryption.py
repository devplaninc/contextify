"""Real PostgreSQL and encryption coverage; set TEST_POSTGRES_URL to a test DB."""
import asyncio
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import insert, text

from dev_observer.api.types.tokens_pb2 import AuthTokenProvider, TokensFilter
from dev_observer.common.crypto import Encryptor
from dev_observer.server.services.health import HealthService
from dev_observer.storage.postgresql.model import AuthTokenEntity, Base, GlobalConfigEntity
from dev_observer.storage.postgresql.provider import PostgresqlStorageProvider


@pytest.mark.parametrize("method", ["list_tokens", "find_tokens"])
def test_bulk_decryption_keeps_health_responsive(method):
    url = os.environ.get("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Set TEST_POSTGRES_URL to run with a real test PostgreSQL database")

    async def run():
        schema = f"token_test_{uuid4().hex}"
        encryptor = Encryptor("test-only-secret")
        store = PostgresqlStorageProvider(url, encryptor)
        engine = store._engine
        engine.update_execution_options(schema_translate_map={None: schema})
        now = datetime.now(timezone.utc)
        rows = []
        for i in range(129):
            token_id = str(uuid4())
            rows.append({
                "id": token_id,
                "namespace": "test",
                "provider": AuthTokenProvider.JIRA,
                "workspace": "target" if i < 128 else "other",
                "system": True,
                "repo": None,
                "token": encryptor.encrypt(f"token-{i}", token_id),
                "expires_at": now - timedelta(days=1),
                "created_at": now,
                "updated_at": now,
            })

        pending = None
        try:
            async with engine.begin() as connection:
                await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
                await connection.run_sync(lambda conn: Base.metadata.create_all(
                    conn, tables=[AuthTokenEntity.__table__, GlobalConfigEntity.__table__],
                ))
                await connection.execute(insert(AuthTokenEntity), rows)
                await connection.execute(insert(GlobalConfigEntity), {
                    "id": "global_config", "json_data": "{}",
                })

            health = HealthService(store)
            assert await health.live() == {"status": "running"}
            if method == "list_tokens":
                operation = store.list_tokens(TokensFilter(
                    provider=AuthTokenProvider.JIRA, workspace="target",
                ))
            else:
                operation = store.find_tokens(AuthTokenProvider.JIRA, workspace="target")
            pending = asyncio.create_task(operation)

            # Include scheduler delay: an event-loop stall must not be hidden by
            # starting the stopwatch only after the health coroutine resumes.
            latencies = []
            while not pending.done():
                started = asyncio.get_running_loop().time()
                await asyncio.sleep(0.05)
                assert await health.live() == {"status": "running"}
                latencies.append(asyncio.get_running_loop().time() - started)

            tokens = await pending
            assert max(latencies) < 1.0, latencies
            assert len(tokens) == 128
            assert {token.token for token in tokens} == {f"token-{i}" for i in range(128)}
            assert all(token.system and token.workspace == "target" for token in tokens)
            # Preserve the existing contract, including expired tokens.
            assert all(token.expires_at.ToDatetime(timezone.utc) == now - timedelta(days=1)
                       for token in tokens)
        finally:
            if pending is not None and not pending.done():
                await pending
            async with engine.begin() as connection:
                await connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            await engine.dispose()

    asyncio.run(run())

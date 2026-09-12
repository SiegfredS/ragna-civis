import anyio.to_thread
import pytest


@pytest.fixture(autouse=True)
def run_sync_tools_without_worker_threads(monkeypatch):
    async def run_sync(function, *args, **kwargs):
        return function(*args, **kwargs)

    # The locked test environment cannot start AnyIO worker threads. Keep the
    # MCPServer public invocation path while making the test deterministic.
    monkeypatch.setattr(anyio.to_thread, "run_sync", run_sync)

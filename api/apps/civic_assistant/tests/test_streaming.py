import asyncio
import json

import pytest

from apps.civic_assistant import streaming
from apps.civic_assistant.streaming import stream_civic_assistant_ndjson


class FakeRuntime:
    def __init__(self, events=(), error=None):
        self.events = events
        self.error = error
        self.closed = False

    async def stream(self, *, message):
        assert message == "Hello"
        try:
            for event in self.events:
                yield event
            if self.error is not None:
                raise self.error
        finally:
            self.closed = True


async def collect_chunks(runtime):
    return [chunk async for chunk in stream_civic_assistant_ndjson(runtime=runtime, message="Hello")]


def decode_events(chunks):
    return [json.loads(chunk) for chunk in chunks]


class TestStreamCivicAssistantNDJSON:
    def test_emits_deltas_and_one_done_event(self):
        runtime = FakeRuntime(
            events=[
                {"type": "delta", "text": "Hello"},
                {"type": "delta", "text": " world"},
            ]
        )

        chunks = asyncio.run(collect_chunks(runtime))

        assert decode_events(chunks) == [
            {"type": "delta", "text": "Hello"},
            {"type": "delta", "text": " world"},
            {"type": "done"},
        ]
        assert runtime.closed

    @pytest.mark.parametrize(
        "event",
        [
            {"type": "private", "text": "secret"},
            {"type": "delta", "text": ""},
            {"type": "delta", "text": 123},
        ],
    )
    def test_invalid_internal_events_emit_only_a_sanitized_error(self, event):
        runtime = FakeRuntime(events=[event])

        chunks = asyncio.run(collect_chunks(runtime))
        output = b"".join(chunks).decode()

        assert decode_events(chunks) == [
            {
                "type": "error",
                "code": "assistant_unavailable",
                "message": "The assistant could not finish. Please try again.",
            }
        ]
        assert "secret" not in output
        assert '"type":"done"' not in output
        assert runtime.closed

    def test_internal_exception_text_is_not_exposed_and_done_is_omitted(self):
        runtime = FakeRuntime(
            events=[{"type": "delta", "text": "Hello"}],
            error=RuntimeError("provider secret and prompt details"),
        )

        chunks = asyncio.run(collect_chunks(runtime))
        output = b"".join(chunks).decode()

        assert decode_events(chunks)[-1] == {
            "type": "error",
            "code": "assistant_unavailable",
            "message": "The assistant could not finish. Please try again.",
        }
        assert "provider secret" not in output
        assert '"type":"done"' not in output
        assert runtime.closed

    def test_cancelled_error_propagates_without_public_error(self):
        runtime = FakeRuntime(error=asyncio.CancelledError())

        with pytest.raises(asyncio.CancelledError):
            asyncio.run(collect_chunks(runtime))

        assert runtime.closed

    def test_response_text_limit_counts_utf8_bytes(self, monkeypatch):
        monkeypatch.setattr(streaming, "MAX_RESPONSE_TEXT_BYTES", len("é".encode("utf-8")))
        runtime = FakeRuntime(events=[{"type": "delta", "text": "é"}])

        chunks = asyncio.run(collect_chunks(runtime))

        assert decode_events(chunks) == [{"type": "delta", "text": "é"}, {"type": "done"}]

    def test_response_limit_closes_runtime_and_emits_error(self, monkeypatch):
        monkeypatch.setattr(streaming, "MAX_RESPONSE_TEXT_BYTES", 2)
        runtime = FakeRuntime(events=[{"type": "delta", "text": "éé"}])

        chunks = asyncio.run(collect_chunks(runtime))

        assert decode_events(chunks) == [
            {
                "type": "error",
                "code": "assistant_unavailable",
                "message": "The assistant could not finish. Please try again.",
            }
        ]
        assert runtime.closed

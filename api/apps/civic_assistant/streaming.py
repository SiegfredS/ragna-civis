import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import aclosing

from apps.civic_assistant.runtime import CivicAssistantRuntime

logger = logging.getLogger(__name__)

MAX_RESPONSE_TEXT_BYTES = 32 * 1024

ASSISTANT_ERROR_EVENT = {
    "type": "error",
    "code": "assistant_unavailable",
    "message": "The assistant could not finish. Please try again.",
}


def encode_ndjson_event(event: dict[str, str]) -> bytes:
    """Encode one Civic Assistant event as UTF-8 NDJSON."""

    return (
        json.dumps(
            event,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


async def stream_civic_assistant_ndjson(*, runtime: CivicAssistantRuntime, message: str) -> AsyncIterator[bytes]:
    """Stream bounded Civic Assistant events as NDJSON."""
    response_text_bytes = 0

    try:
        async with aclosing(runtime.stream(message=message)) as events:
            async for event in events:
                if event["type"] != "delta":
                    raise ValueError("Unexpected Civic Assistant stream event.")

                text = event["text"]
                if not isinstance(text, str) or not text:
                    raise ValueError("Invalid Civic Assistant stream text.")

                response_text_bytes += len(text.encode("utf-8"))

                if response_text_bytes > MAX_RESPONSE_TEXT_BYTES:
                    raise ValueError("Assistant output limit exceeded.")

                yield encode_ndjson_event(
                    {
                        "type": "delta",
                        "text": text,
                    }
                )
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.warning("Civic Assistant stream failed.")
        yield encode_ndjson_event(ASSISTANT_ERROR_EVENT)
        return

    yield encode_ndjson_event({"type": "done"})

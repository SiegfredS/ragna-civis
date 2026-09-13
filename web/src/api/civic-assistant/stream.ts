import { fetchWithAuth } from "../client";

import {
  civicAssistantStreamEventSchema,
  type CivicAssistantStreamEvent,
} from "./schemas";

type StreamCivicAssistantAnswerOptions = {
  message: string;
  signal: AbortSignal;
  onEvent: (event: CivicAssistantStreamEvent) => void;
};

function parseEvent(line: string): CivicAssistantStreamEvent {
  let record: unknown;

  try {
    record = JSON.parse(line);
  } catch {
    throw new Error("The assistant returned an invalid response.");
  }

  return civicAssistantStreamEventSchema.parse(record);
}

export async function streamCivicAssistantAnswer({
  message,
  signal,
  onEvent,
}: StreamCivicAssistantAnswerOptions) {
  const response = await fetchWithAuth("/api/civic-assistant/chat/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
    signal,
  });

  if (!response.headers.get("content-type")?.includes("application/x-ndjson")) {
    throw new Error("The assistant returned an unexpected response.");
  }

  if (!response.body) {
    throw new Error("The assistant response could not be read.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8", { fatal: true });
  let buffer = "";
  let terminalEventReceived = false;

  function handleLine(line: string) {
    if (!line.trim()) {
      return;
    }

    if (terminalEventReceived) {
      throw new Error("The assistant returned events after completion.");
    }

    const event = parseEvent(line);
    onEvent(event);

    if (event.type !== "delta") {
      terminalEventReceived = true;
    }
  }

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        handleLine(line.endsWith("\r") ? line.slice(0, -1) : line);
      }
    }

    buffer += decoder.decode();

    if (buffer.trim()) {
      handleLine(buffer.endsWith("\r") ? buffer.slice(0, -1) : buffer);
    }

    if (!terminalEventReceived) {
      throw new Error("The assistant response ended before completion.");
    }
  } finally {
    await reader.cancel().catch(() => undefined);
    reader.releaseLock();
  }
}

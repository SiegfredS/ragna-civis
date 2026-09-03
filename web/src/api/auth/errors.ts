export class ApiError extends Error {
  readonly status: number;
  readonly details: unknown;

  constructor(status: number, details: unknown) {
    super(`API request failed with status ${status}.`);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

const defaultErrorMessage =
  "We couldn't complete that request. Please try again.";

function getStatusErrorMessage(status: number) {
  if (status === 400) {
    return "Please check the information provided and try again.";
  }

  if (status === 401) {
    return "Your session is not authorized. Please sign in again.";
  }

  if (status === 403) {
    return "You don't have permission to perform that action.";
  }

  if (status === 404) {
    return "The requested resource could not be found.";
  }

  if (status === 429) {
    return "Too many requests were made. Please try again shortly.";
  }

  if (status >= 500) {
    return "The service is temporarily unavailable. Please try again later.";
  }

  return defaultErrorMessage;
}

function isSafeMessage(value: string) {
  const normalizedValue = value.trim().toLowerCase();

  return (
    normalizedValue.length > 0 &&
    !normalizedValue.includes("<html") &&
    !normalizedValue.includes("<!doctype") &&
    !normalizedValue.includes("traceback") &&
    !normalizedValue.includes("stack trace") &&
    !normalizedValue.includes("django version")
  );
}

function getDetailsMessage(
  details: unknown,
  visited = new Set<unknown>(),
): string | undefined {
  if (typeof details === "string") {
    return isSafeMessage(details) ? details.trim() : undefined;
  }

  if (typeof details !== "object" || details === null || visited.has(details)) {
    return undefined;
  }

  visited.add(details);

  if (Array.isArray(details)) {
    for (const detail of details) {
      const message = getDetailsMessage(detail, visited);
      if (message) {
        return message;
      }
    }

    return undefined;
  }

  const values = details as Record<string, unknown>;
  const messageKeys = [
    "detail",
    "message",
    "error",
    "nonFieldErrors",
    "non_field_errors",
  ];

  for (const key of messageKeys) {
    const message = getDetailsMessage(values[key], visited);
    if (message) {
      return message;
    }
  }

  for (const value of Object.values(values)) {
    const message = getDetailsMessage(value, visited);
    if (message) {
      return message;
    }
  }

  return undefined;
}

export function getApiErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    return (
      getDetailsMessage(error.details) ?? getStatusErrorMessage(error.status)
    );
  }

  return defaultErrorMessage;
}

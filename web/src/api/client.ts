import { z } from "zod";

import { ApiError } from "./auth/errors";

export { ApiError, getApiErrorMessage } from "./auth/errors";

export const AUTH_TOKEN_KEY = "ragna-civis.auth-token";

type ApiSearchParamValue =
  string | number | boolean | string[] | number[] | undefined;

export type ApiSearchParams = Record<string, ApiSearchParamValue>;

export const apiSearchParamsSchema = z.record(
  z.string(),
  z.union([
    z.string(),
    z.number(),
    z.boolean(),
    z.array(z.string()),
    z.array(z.number()),
    z.undefined(),
  ]),
);

const apiBaseUrl = z
  .string()
  .trim()
  .min(1, "VITE_API_BASE_URL must be set.")
  .transform((value) => value.replace(/\/+$/, ""))
  .parse(import.meta.env.VITE_API_BASE_URL);

type ApiRequestInit = RequestInit & {
  searchParams?: ApiSearchParams;
};

type FetchWithAuthOptions = ApiRequestInit & {
  token?: string | null;
};

export type RequestJsonOptions<T> = Omit<ApiRequestInit, "body"> & {
  body?: unknown;
  schema: z.ZodType<T>;
  token?: string | null;
};

export function getStoredAuthToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setStoredAuthToken(token: string) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function removeStoredAuthToken() {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(AUTH_TOKEN_KEY);
}

function buildUrl(path: string, searchParams?: ApiSearchParams) {
  const url = new URL(
    `${apiBaseUrl}${path.startsWith("/") ? path : `/${path}`}`,
  );

  if (!searchParams) {
    return url;
  }

  const parsedSearchParams = apiSearchParamsSchema.parse(searchParams);

  for (const [key, value] of Object.entries(parsedSearchParams)) {
    if (value === undefined) {
      continue;
    }

    url.searchParams.set(
      key,
      Array.isArray(value) ? value.join(",") : String(value),
    );
  }

  return url;
}

async function parseResponseBody(response: Response): Promise<unknown> {
  if (response.status === 204) {
    return undefined;
  }

  if (response.headers.get("content-type")?.includes("json")) {
    try {
      return await response.json();
    } catch {
      return undefined;
    }
  }

  return response.text();
}

export async function fetchAPI(
  path: string,
  { searchParams, ...init }: ApiRequestInit = {},
) {
  return fetch(buildUrl(path, searchParams), init);
}

export async function fetchWithAuth(
  path: string,
  { token, ...init }: FetchWithAuthOptions = {},
) {
  const authToken = token ?? getStoredAuthToken();
  const headers = new Headers(init.headers);

  if (authToken) {
    headers.set("Authorization", `Token ${authToken}`);
  }

  const response = await fetchAPI(path, { ...init, headers });

  if (!response.ok) {
    throw new ApiError(response.status, await parseResponseBody(response));
  }

  return response;
}

export async function requestJson<T>(
  path: string,
  options: RequestJsonOptions<T>,
): Promise<T> {
  const { body, headers: providedHeaders, schema, token, ...init } = options;
  const headers = new Headers(providedHeaders);

  if (body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetchWithAuth(path, {
    ...init,
    body: body === undefined ? undefined : JSON.stringify(body),
    headers,
    token,
  });

  return schema.parse(await parseResponseBody(response));
}

import { queryOptions } from "@tanstack/react-query";

import { removeStoredAuthToken, requestJson } from "../client";

import { ApiError } from "./errors";
import { authKeys } from "./keys";
import { meSchema } from "./schemas";

async function fetchMe() {
  try {
    return await requestJson("/api/user-profiles/me/", { schema: meSchema });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      removeStoredAuthToken();
    }

    throw error;
  }
}

export const meQueryOptions = () =>
  queryOptions({
    queryKey: authKeys.me(),
    queryFn: fetchMe,
    retry: false,
  });

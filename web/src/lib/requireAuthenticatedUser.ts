import { redirect } from "@tanstack/react-router";

import {
  ApiError,
  authKeys,
  getStoredAuthToken,
  meQueryOptions,
} from "@/api/auth";
import { queryClient } from "@/api/queryClient";

export async function requireAuthenticatedUser() {
  if (!getStoredAuthToken()) {
    throw redirect({ to: "/login" });
  }

  try {
    await queryClient.fetchQuery(meQueryOptions());
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      queryClient.removeQueries({ queryKey: authKeys.me() });
      throw redirect({ to: "/login" });
    }

    throw error;
  }
}

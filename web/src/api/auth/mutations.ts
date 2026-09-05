import { mutationOptions } from "@tanstack/react-query";

import { fetchWithAuth } from "../client";

export const logoutMutationOptions = () =>
  mutationOptions({
    mutationFn: async () => {
      await fetchWithAuth("/api/auth/logout/", { method: "POST" });
    },
  });

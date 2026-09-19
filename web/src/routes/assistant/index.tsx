import { createFileRoute } from "@tanstack/react-router";

import { requireAuthenticatedUser } from "@/lib/requireAuthenticatedUser";

export const Route = createFileRoute("/assistant/")({
  beforeLoad: requireAuthenticatedUser,
});

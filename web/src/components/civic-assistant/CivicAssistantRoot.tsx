import type { ReactNode } from "react";

import { useQuery } from "@tanstack/react-query";
import { useLocation } from "@tanstack/react-router";

import { getStoredAuthToken, meQueryOptions } from "@/api/auth";

import { CIVIC_ASSISTANT_SESSION_STATUS } from "./constants";
import { CivicAssistantLauncher } from "./CivicAssistantLauncher";
import { CivicAssistantProvider } from "./CivicAssistantProvider";
import type { CivicAssistantSession } from "./types";

export function CivicAssistantRoot({ children }: { children: ReactNode }) {
  const pathname = useLocation({ select: (location) => location.pathname });
  const token = getStoredAuthToken();
  const { data: me, isSuccess } = useQuery({
    ...meQueryOptions(),
    enabled: Boolean(token),
  });
  const session: CivicAssistantSession = !token
    ? { status: CIVIC_ASSISTANT_SESSION_STATUS.SIGNED_OUT }
    : isSuccess && me
      ? {
          status: CIVIC_ASSISTANT_SESSION_STATUS.AUTHENTICATED,
          userId: me.id,
        }
      : { status: CIVIC_ASSISTANT_SESSION_STATUS.CHECKING };
  const isExcludedRoute =
    pathname === "/login" ||
    pathname === "/login/" ||
    pathname === "/assistant" ||
    pathname === "/assistant/";
  const showLauncher =
    session.status === CIVIC_ASSISTANT_SESSION_STATUS.AUTHENTICATED &&
    !isExcludedRoute;

  return (
    <CivicAssistantProvider session={session}>
      {children}
      {showLauncher && <CivicAssistantLauncher />}
    </CivicAssistantProvider>
  );
}

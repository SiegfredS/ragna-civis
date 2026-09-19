import { createContext } from "react";

import type { CivicAssistantMessage } from "./types";

export type CivicAssistantContextValue = {
  messages: CivicAssistantMessage[];
  error: string | null;
  isSubmitting: boolean;
  submitMessage: (message: string) => boolean;
};

export const CivicAssistantContext =
  createContext<CivicAssistantContextValue | null>(null);

import { useContext } from "react";

import { CivicAssistantContext } from "../CivicAssistantContext";

export function useCivicAssistant() {
  const context = useContext(CivicAssistantContext);

  if (!context) {
    throw new Error(
      "useCivicAssistant must be used within a CivicAssistantProvider.",
    );
  }

  return context;
}

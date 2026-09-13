import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { FormProvider, useForm } from "react-hook-form";

import {
  ApiError,
  authKeys,
  getApiErrorMessage,
  removeStoredAuthToken,
} from "@/api/auth";
import { streamCivicAssistantAnswer } from "@/api/civic-assistant/stream";
import { queryClient } from "@/api/queryClient";

import { CivicAssistantContext } from "./CivicAssistantContext";
import {
  CIVIC_ASSISTANT_ROLE,
  CIVIC_ASSISTANT_SESSION_STATUS,
} from "./constants";
import type {
  CivicAssistantFormValues,
  CivicAssistantMessage,
  CivicAssistantSession,
} from "./types";

export function CivicAssistantProvider({
  children,
  session,
}: {
  children: ReactNode;
  session: CivicAssistantSession;
}) {
  const [messages, setMessages] = useState<CivicAssistantMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const form = useForm<CivicAssistantFormValues>({
    defaultValues: {
      message: "",
    },
  });
  const activeControllerRef = useRef<AbortController | null>(null);
  const activeRequestIdRef = useRef<string | null>(null);
  const authenticatedUserIdRef = useRef<number | null>(null);

  const invalidateActiveRequest = useCallback(() => {
    activeRequestIdRef.current = null;
    activeControllerRef.current?.abort();
    activeControllerRef.current = null;
    setIsSubmitting(false);
  }, []);

  useEffect(() => invalidateActiveRequest, [invalidateActiveRequest]);

  const sessionUserId =
    session.status === CIVIC_ASSISTANT_SESSION_STATUS.AUTHENTICATED
      ? session.userId
      : null;

  useEffect(() => {
    if (session.status === CIVIC_ASSISTANT_SESSION_STATUS.CHECKING) {
      return;
    }

    const authenticatedUserChanged =
      sessionUserId !== null &&
      authenticatedUserIdRef.current !== null &&
      authenticatedUserIdRef.current !== sessionUserId;

    if (sessionUserId !== null && !authenticatedUserChanged) {
      authenticatedUserIdRef.current = sessionUserId;
      return;
    }

    authenticatedUserIdRef.current = sessionUserId;
    invalidateActiveRequest();
    setMessages([]);
    setError(null);
    form.reset();
  }, [form, invalidateActiveRequest, session.status, sessionUserId]);

  const submitMessage = useCallback((message: string) => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || activeRequestIdRef.current) {
      return false;
    }

    const requestId = crypto.randomUUID();
    const userMessageId = crypto.randomUUID();
    const assistantMessageId = crypto.randomUUID();
    const controller = new AbortController();

    activeRequestIdRef.current = requestId;
    activeControllerRef.current = controller;
    setError(null);
    setIsSubmitting(true);
    setMessages((current) => [
      ...current,
      {
        id: userMessageId,
        role: CIVIC_ASSISTANT_ROLE.USER,
        text: trimmedMessage,
      },
      {
        id: assistantMessageId,
        role: CIVIC_ASSISTANT_ROLE.ASSISTANT,
        text: "",
      },
    ]);

    function removeEmptyAssistantMessage() {
      setMessages((current) =>
        current.filter(
          (currentMessage) =>
            currentMessage.id !== assistantMessageId || currentMessage.text,
        ),
      );
    }

    void streamCivicAssistantAnswer({
      message: trimmedMessage,
      signal: controller.signal,
      onEvent: (event) => {
        if (activeRequestIdRef.current !== requestId) {
          return;
        }

        if (event.type === "delta") {
          setMessages((current) =>
            current.map((currentMessage) =>
              currentMessage.id === assistantMessageId
                ? {
                    ...currentMessage,
                    text: currentMessage.text + event.text,
                  }
                : currentMessage,
            ),
          );
          return;
        }

        if (event.type === "error") {
          setError(event.message);
          removeEmptyAssistantMessage();
        }
      },
    })
      .catch((streamError: unknown) => {
        if (
          activeRequestIdRef.current !== requestId ||
          controller.signal.aborted
        ) {
          return;
        }

        if (streamError instanceof ApiError && streamError.status === 401) {
          removeStoredAuthToken();
          queryClient.removeQueries({ queryKey: authKeys.me() });
          return;
        }

        removeEmptyAssistantMessage();
        setError(getApiErrorMessage(streamError));
      })
      .finally(() => {
        if (activeRequestIdRef.current !== requestId) {
          return;
        }

        activeRequestIdRef.current = null;
        activeControllerRef.current = null;
        setIsSubmitting(false);
      });

    return true;
  }, []);

  return (
    <CivicAssistantContext.Provider
      value={{ messages, error, isSubmitting, submitMessage }}
    >
      <FormProvider {...form}>{children}</FormProvider>
    </CivicAssistantContext.Provider>
  );
}

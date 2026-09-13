import { CIVIC_ASSISTANT_ROLE } from "./constants";
import { CivicAssistantComposer } from "./CivicAssistantComposer";
import { CivicAssistantMarkdown } from "./CivicAssistantMarkdown";
import { useCivicAssistant } from "./hooks/useCivicAssistant";

type CivicAssistantChatProps = {
  mode: "compact" | "page";
};

export function CivicAssistantChat({ mode }: CivicAssistantChatProps) {
  const { error, isSubmitting, messages } = useCivicAssistant();

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div
        className={
          mode === "compact"
            ? "min-h-0 flex-1 overflow-y-auto p-4"
            : "min-h-0 flex-1 overflow-y-auto p-6"
        }
        role="region"
        aria-label="Civic Assistant messages"
        aria-busy={isSubmitting}
      >
        {messages.length === 0 ? (
          <div className="space-y-2 text-sm text-muted-foreground">
            <p className="font-medium text-foreground">
              Ask a question about Ragna Civis organizations.
            </p>
            <p>
              The Civic Assistant can help you find information from available
              organization records.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <article key={message.id} className="space-y-1">
                <p className="text-sm font-medium">
                  {message.role === CIVIC_ASSISTANT_ROLE.USER
                    ? "You"
                    : "Civic Assistant"}
                </p>
                {message.text &&
                message.role === CIVIC_ASSISTANT_ROLE.ASSISTANT ? (
                  <CivicAssistantMarkdown>
                    {message.text}
                  </CivicAssistantMarkdown>
                ) : message.text ? (
                  <p className="whitespace-pre-wrap break-words text-sm">
                    {message.text}
                  </p>
                ) : isSubmitting &&
                  message.role === CIVIC_ASSISTANT_ROLE.ASSISTANT ? (
                  <p className="text-sm text-muted-foreground">Thinking…</p>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </div>
      {isSubmitting && (
        <p
          className="px-4 pb-2 text-sm text-muted-foreground"
          aria-live="polite"
        >
          Generating a response…
        </p>
      )}
      {error && (
        <p className="mx-4 mb-4 text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
      <div className="border-t">
        <CivicAssistantComposer />
      </div>
    </div>
  );
}

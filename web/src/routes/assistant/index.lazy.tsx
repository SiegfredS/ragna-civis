import { createLazyFileRoute } from "@tanstack/react-router";

import { CivicAssistantChat } from "@/components/civic-assistant/CivicAssistantChat";

export const Route = createLazyFileRoute("/assistant/")({
  component: CivicAssistantPage,
});

function CivicAssistantPage() {
  return (
    <section className="mx-auto flex h-[calc(100dvh-10rem)] w-full max-w-3xl flex-col">
      <div className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">
          Civic Assistant
        </h1>
        <p className="text-muted-foreground">
          Ask questions about organizations available in Ragna Civis.
        </p>
      </div>

      <div className="mt-6 flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border">
        <CivicAssistantChat mode="page" />
      </div>
    </section>
  );
}

import { createLazyFileRoute } from "@tanstack/react-router";

export const Route = createLazyFileRoute("/governance/")({
  component: GovernancePage,
});

function GovernancePage() {
  return (
    <div className="space-y-2">
      <h1 className="text-3xl font-semibold tracking-tight">Governance</h1>

      <p className="text-muted-foreground">
        Governance information will live here.
      </p>
    </div>
  );
}

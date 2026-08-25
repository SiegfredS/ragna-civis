import { createLazyFileRoute } from "@tanstack/react-router";

export const Route = createLazyFileRoute("/")({
  component: OverviewPage,
});

function OverviewPage() {
  return (
    <div className="space-y-2">
      <h1 className="text-3xl font-semibold tracking-tight">Civic Overview</h1>

      <p className="text-muted-foreground">
        Explore governance, public projects, and civic information.
      </p>
    </div>
  );
}

import { createLazyFileRoute } from "@tanstack/react-router";

export const Route = createLazyFileRoute("/analytics/")({
  component: AnalyticsPage,
});

function AnalyticsPage() {
  return (
    <div className="space-y-2">
      <h1 className="text-3xl font-semibold tracking-tight">Analytics</h1>

      <p className="text-muted-foreground">
        Civic analytics and reporting will live here.
      </p>
    </div>
  );
}

import { createLazyFileRoute } from "@tanstack/react-router";

export const Route = createLazyFileRoute("/projects/")({
  component: ProjectsPage,
});

function ProjectsPage() {
  return (
    <div className="space-y-2">
      <h1 className="text-3xl font-semibold tracking-tight">Public Projects</h1>

      <p className="text-muted-foreground">
        Public project information will live here.
      </p>
    </div>
  );
}

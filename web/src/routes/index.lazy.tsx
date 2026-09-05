import { Link, createLazyFileRoute } from "@tanstack/react-router";

import { buttonVariants } from "@/components/ui/button";

export const Route = createLazyFileRoute("/")({
  component: OverviewPage,
});

function OverviewPage() {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-10rem)] max-w-3xl items-center">
      <div className="space-y-6">
        <p className="text-sm font-semibold tracking-[0.2em] text-muted-foreground uppercase">
          Ragna Civis
        </p>

        <h1 className="max-w-2xl text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
          A clearer view of the decisions that shape your community.
        </h1>

        <p className="max-w-xl text-lg leading-8 text-muted-foreground">
          Follow public governance and projects in one accountable, accessible
          place.
        </p>

        <div className="flex flex-wrap gap-3">
          <Link to="/login" className={buttonVariants({ size: "lg" })}>
            Sign in
          </Link>

          <Link
            to="/governance"
            className={buttonVariants({ size: "lg", variant: "outline" })}
          >
            Explore governance
          </Link>
        </div>
      </div>
    </section>
  );
}

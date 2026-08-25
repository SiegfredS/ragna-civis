import { Outlet, createRootRoute } from "@tanstack/react-router";

import { AppHeader } from "@/components/navigation/AppHeader";
import { AppSidebar } from "@/components/navigation/AppSidebar";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <AppHeader />

      <div className="flex flex-1">
        <AppSidebar />

        <main className="min-w-0 flex-1 p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

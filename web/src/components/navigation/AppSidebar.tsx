import { Link } from "@tanstack/react-router";

import { navigationItems } from "@/navigation";

export function AppSidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r md:block">
      <nav className="space-y-1 p-4">
        {navigationItems.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            activeOptions={{
              exact: item.to === "/",
            }}
            className="block rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
            activeProps={{
              className: "bg-accent font-medium text-accent-foreground",
            }}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

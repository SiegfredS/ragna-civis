import { useState } from "react";

import { Link } from "@tanstack/react-router";
import { Menu } from "lucide-react";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { navigationItems } from "@/navigation";

export function AppHeader() {
  const [isNavigationOpen, setIsNavigationOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center border-b bg-background px-4">
      <Sheet open={isNavigationOpen} onOpenChange={setIsNavigationOpen}>
        <SheetTrigger
          className="mr-3 inline-flex size-9 items-center justify-center rounded-md hover:bg-accent md:hidden"
          aria-label="Open navigation"
        >
          <Menu className="size-5" />
        </SheetTrigger>

        <SheetContent side="left" className="w-72">
          <SheetHeader>
            <SheetTitle>Ragna Civis</SheetTitle>
          </SheetHeader>

          <nav className="space-y-1 px-4">
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
                onClick={() => setIsNavigationOpen(false)}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </SheetContent>
      </Sheet>

      <Link to="/" className="font-semibold tracking-tight">
        Ragna Civis
      </Link>
    </header>
  );
}

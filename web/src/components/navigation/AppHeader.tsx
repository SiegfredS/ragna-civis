import { useEffect, useState } from "react";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, useLocation, useRouter } from "@tanstack/react-router";
import { Menu } from "lucide-react";

import {
  ApiError,
  authKeys,
  getApiErrorMessage,
  getStoredAuthToken,
  logoutMutationOptions,
  meQueryOptions,
  removeStoredAuthToken,
} from "@/api/auth";
import { queryClient } from "@/api/queryClient";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { navigationItems } from "@/navigation";

export function AppHeader() {
  const router = useRouter();
  // Re-read the stored token when navigation follows a successful login.
  useLocation({ select: (location) => location.href });
  const [isNavigationOpen, setIsNavigationOpen] = useState(false);
  const token = getStoredAuthToken();
  const { data: me, error } = useQuery({
    ...meQueryOptions(),
    enabled: Boolean(token),
  });
  const logoutMutation = useMutation(logoutMutationOptions());
  const isUnauthorized = error instanceof ApiError && error.status === 401;

  useEffect(() => {
    if (isUnauthorized) {
      queryClient.removeQueries({ queryKey: authKeys.me() });
    }
  }, [isUnauthorized]);

  async function handleLogout() {
    logoutMutation.reset();

    try {
      await logoutMutation.mutateAsync();
      removeStoredAuthToken();
      queryClient.removeQueries({ queryKey: authKeys.me() });
      await router.navigate({ to: "/" });
    } catch {
      // Keep the token and authenticated query state so the user can retry.
    }
  }

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

      <div className="ml-auto flex items-center gap-3">
        {logoutMutation.error && (
          <p className="text-sm text-destructive" role="alert">
            {getApiErrorMessage(logoutMutation.error)}
          </p>
        )}

        {me ? (
          <>
            <p className="text-sm text-muted-foreground">Hi {me.username}</p>
            <Button
              type="button"
              size="sm"
              variant="outline"
              disabled={logoutMutation.isPending}
              onClick={handleLogout}
            >
              {logoutMutation.isPending ? "Logging out…" : "Log out"}
            </Button>
          </>
        ) : token ? (
          <span className="text-sm text-muted-foreground" aria-live="polite">
            Checking session…
          </span>
        ) : (
          <Link
            to="/login"
            className={buttonVariants({ size: "sm", variant: "outline" })}
          >
            Sign in
          </Link>
        )}
      </div>
    </header>
  );
}

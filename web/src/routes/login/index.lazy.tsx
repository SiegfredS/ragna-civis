import { useForm } from "react-hook-form";

import { Link, createLazyFileRoute, useRouter } from "@tanstack/react-router";

import { Button, buttonVariants } from "@/components/ui/button";
import {
  getApiErrorMessage,
  loginResponseSchema,
  setStoredAuthToken,
} from "@/api/auth";
import { requestJson } from "@/api/client";

type LoginFormValues = {
  username: string;
  password: string;
};

export const Route = createLazyFileRoute("/login/")({
  component: LoginPage,
});

function LoginPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>();

  async function onSubmit(values: LoginFormValues) {
    let response;

    try {
      response = await requestJson("/api/auth/login/", {
        body: values,
        method: "POST",
        schema: loginResponseSchema,
      });
    } catch (error) {
      setError("root", { message: getApiErrorMessage(error) });
      return;
    }

    try {
      setStoredAuthToken(response.token);
      await router.navigate({ to: "/" });
    } catch {
      setError("root", {
        message:
          "You signed in, but we couldn't finish setting up your session.",
      });
    }
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-10rem)] max-w-md items-center">
      <div className="w-full space-y-6">
        <div className="space-y-2">
          <p className="text-sm font-semibold tracking-[0.2em] text-muted-foreground uppercase">
            Ragna Civis
          </p>
          <h1 className="text-3xl font-semibold tracking-tight">Sign in</h1>
          <p className="text-muted-foreground">
            Use your Ragna Civis username or email and password.
          </p>
        </div>

        <form
          className="space-y-5"
          onSubmit={handleSubmit(onSubmit)}
          noValidate
        >
          {errors.root?.message && (
            <p
              className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
              role="alert"
            >
              {errors.root.message}
            </p>
          )}

          <div className="space-y-2">
            <label htmlFor="username" className="text-sm font-medium">
              Username or email
            </label>
            <input
              id="username"
              autoComplete="username"
              aria-describedby={errors.username ? "username-error" : undefined}
              aria-invalid={Boolean(errors.username)}
              className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 aria-invalid:border-destructive"
              {...register("username", {
                required: "Enter your username or email.",
              })}
            />
            {errors.username?.message && (
              <p id="username-error" className="text-sm text-destructive">
                {errors.username.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              aria-describedby={errors.password ? "password-error" : undefined}
              aria-invalid={Boolean(errors.password)}
              className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 aria-invalid:border-destructive"
              {...register("password", { required: "Enter your password." })}
            />
            {errors.password?.message && (
              <p id="password-error" className="text-sm text-destructive">
                {errors.password.message}
              </p>
            )}
          </div>

          <Button type="submit" size="lg" disabled={isSubmitting}>
            {isSubmitting ? "Signing in…" : "Sign in"}
          </Button>
        </form>

        <Link
          to="/"
          className={buttonVariants({ variant: "link", className: "px-0" })}
        >
          Return to overview
        </Link>
      </div>
    </section>
  );
}

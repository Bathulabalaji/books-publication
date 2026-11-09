import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { routes } from "./routes";

function renderAt(path: string, routeObjects = routes) {
  const router = createMemoryRouter(routeObjects, { initialEntries: [path] });
  return render(<RouterProvider router={router} />);
}

describe("application routes", () => {
  it("renders a semantic and keyboard-skippable PUSTORA landing shell", () => {
    renderAt("/");

    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Main navigation" })).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveAttribute("id", "main-content");
    expect(screen.getByRole("heading", { name: /find a little more wonder/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Skip to content" })).toHaveAttribute(
      "href",
      "#main-content",
    );
  });

  it("renders a not-found page and returns to the home route", async () => {
    const user = userEvent.setup();
    renderAt("/missing-page");

    expect(screen.getByRole("heading", { name: "This page wandered off." })).toBeInTheDocument();
    await user.click(screen.getByRole("link", { name: "Return home" }));
    expect(await screen.findByRole("heading", { name: /find a little more wonder/i })).toBeVisible();
  });

  it("shows a safe route error without exposing exception details", async () => {
    const failingRoutes = routes.map((route) =>
      route.path === "/"
        ? {
            ...route,
            loader: () => {
              throw new Error("private diagnostic detail");
            },
          }
        : route,
    );
    renderAt("/", failingRoutes);

    expect(await screen.findByRole("heading", { name: "We couldn’t open this page." })).toBeVisible();
    expect(screen.queryByText("private diagnostic detail")).not.toBeInTheDocument();
  });
});

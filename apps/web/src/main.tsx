import { StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { RouteLoadingFallback } from "./app/RouteLoadingFallback";
import { routes } from "./app/routes";
import { validatePublicConfig } from "./config/api";
import "./styles.css";

validatePublicConfig();

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("The application root element was not found.");
}

const router = createBrowserRouter(routes);

createRoot(rootElement).render(
  <StrictMode>
    <Suspense fallback={<RouteLoadingFallback />}>
      <RouterProvider router={router} />
    </Suspense>
  </StrictMode>,
);

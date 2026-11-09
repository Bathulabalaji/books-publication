import { Link, type RouteObject } from "react-router-dom";
import { HomePage } from "../pages/home/HomePage";
import { NotFoundPage } from "../pages/NotFoundPage";

export function RouteErrorPage() {
  return (
    <main className="message-page">
      <p className="eyebrow">A little pause</p>
      <h1>We couldn’t open this page.</h1>
      <p className="message-page__copy">
        Something unexpected happened. Please try again or return to the home page.
      </p>
      <Link className="button button--primary" to="/">
        Return home
      </Link>
    </main>
  );
}

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <HomePage />,
    errorElement: <RouteErrorPage />,
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
];

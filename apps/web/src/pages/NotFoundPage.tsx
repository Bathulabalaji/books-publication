import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="message-page">
      <Link aria-label="PUSTORA home" className="brand" to="/">
        <span aria-hidden="true" className="brand__mark">
          p
        </span>
        <span>pustora</span>
      </Link>
      <p className="eyebrow">404 — Page not found</p>
      <h1>This page wandered off.</h1>
      <p className="message-page__copy">
        The page you’re looking for isn’t here. Let’s find our way back.
      </p>
      <Link className="button button--primary" to="/">
        Return home
      </Link>
    </main>
  );
}

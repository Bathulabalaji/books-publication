export function RouteLoadingFallback() {
  return (
    <main className="message-page" aria-live="polite" aria-busy="true">
      <span className="loading-mark" aria-hidden="true" />
      <p className="eyebrow">Opening PUSTORA</p>
    </main>
  );
}

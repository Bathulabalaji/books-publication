const DEFAULT_API_BASE_URL = "/api/v1";

export function resolveApiBaseUrl(value: string | undefined): string {
  if (value === undefined) {
    return DEFAULT_API_BASE_URL;
  }

  const candidate = value.trim();
  if (!candidate || candidate !== value) {
    throw new Error("VITE_API_BASE_URL must be a non-empty URL without surrounding whitespace.");
  }

  if (candidate.startsWith("/")) {
    const url = new URL(candidate, "https://pustora.invalid");
    if (url.origin !== "https://pustora.invalid") {
      throw new Error("VITE_API_BASE_URL must be a same-origin path.");
    }
    if (url.search || url.hash) {
      throw new Error("VITE_API_BASE_URL cannot contain a query string or fragment.");
    }

    return url.pathname.replace(/\/+$/, "") || "/";
  }

  let url: URL;
  try {
    url = new URL(candidate);
  } catch {
    throw new Error("VITE_API_BASE_URL must be an absolute HTTP(S) URL or a same-origin path.");
  }

  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error("VITE_API_BASE_URL must use HTTP or HTTPS.");
  }
  if (url.username || url.password) {
    throw new Error("VITE_API_BASE_URL must not contain credentials.");
  }
  if (url.search || url.hash) {
    throw new Error("VITE_API_BASE_URL cannot contain a query string or fragment.");
  }

  return `${url.origin}${url.pathname.replace(/\/+$/, "")}`;
}

export function validatePublicConfig(): void {
  resolveApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
}

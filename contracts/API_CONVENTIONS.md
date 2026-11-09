# Initial HTTP API conventions

## Versioning and metadata

- Product API routes use `/api/v1/...`; a breaking contract change requires a new major path version.
- FastAPI owns the OpenAPI document at `/openapi.json`. The API title is `PUSTORA API`; `0.1.0` is the current application/API implementation version, not a promise of contract stability beyond these conventions.
- The Phase 0 health endpoint is `GET /api/v1/health`. It reports only service status and configured service name; it is not a dependency readiness or production availability guarantee.
- Unknown routes return a documented 404 error. No product operation is stubbed as a success response.
- Local development uses FastAPI's `/docs` and `/redoc` pages; the machine-readable contract is `/openapi.json`.

## Request correlation

Every HTTP response includes an opaque server-generated UUID in `X-Request-ID`. The matching identifier appears in unexpected-error server logs. The server does not trust or reuse a caller-supplied request ID.

## Error envelope

All expected API errors use:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "request_id": "4b441c08-edc2-42de-aa9f-c5bc02ab949e",
    "details": [
      {
        "location": ["query", "limit"],
        "code": "int_parsing",
        "message": "Invalid value."
      }
    ]
  }
}
```

`details` is present for validation errors only. Its field locations, error codes, and generic messages must not include submitted values. Application errors expose only an intentional stable code/message and appropriate HTTP status. Not-found and method-not-allowed messages are normalized rather than forwarding framework details.

Unexpected errors return HTTP 500 with code `INTERNAL_SERVER_ERROR` and message `An unexpected error occurred.` The public response contains no exception, stack trace, request payload, or secret. Server logs record a request ID, HTTP method, route template, and exception class, but omit exception text and request data to avoid accidental secret disclosure.

## Configuration and security boundary

Backend settings are validated at startup and use the `PUSTORA_` environment prefix. The test app is constructed with explicit test settings. This bootstrap does not require credentials, and no secret-bearing configuration is exposed through routes or OpenAPI. Future authentication and authorization behavior must be implemented in their own services/routes and enforced server-side.

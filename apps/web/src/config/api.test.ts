import { describe, expect, it } from "vitest";
import { resolveApiBaseUrl } from "./api";

describe("resolveApiBaseUrl", () => {
  it("uses a same-origin API path when no environment value is configured", () => {
    expect(resolveApiBaseUrl(undefined)).toBe("/api/v1");
  });

  it("normalizes a valid public HTTP API origin", () => {
    expect(resolveApiBaseUrl("https://api.pustora.in/api/v1/")).toBe(
      "https://api.pustora.in/api/v1",
    );
  });

  it("accepts a same-origin path", () => {
    expect(resolveApiBaseUrl("/backend/api/v1/")).toBe("/backend/api/v1");
  });

  it.each([
    ["empty values", ""],
    ["surrounding whitespace", " https://api.pustora.in"],
    ["protocol-relative URLs", "//api.pustora.in/api"],
    ["backslash-based URL escapes", "/\\api.pustora.in/api"],
    ["unsupported protocols", "javascript:alert(1)"],
    ["credentials", "https://user:password@api.pustora.in"],
    ["query strings", "https://api.pustora.in/api?token=secret"],
    ["fragments", "https://api.pustora.in/api#private"],
  ])("rejects %s", (_description, value) => {
    expect(() => resolveApiBaseUrl(value)).toThrow();
  });
});

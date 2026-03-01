import type { UserRole } from "./api/types";

export function decodeRoleFromJwt(token: string): UserRole | null {
  const segments = token.split(".");
  if (segments.length < 2) {
    return null;
  }
  try {
    const payload = JSON.parse(base64UrlDecode(segments[1])) as { role?: unknown };
    if (
      payload.role === "promoter" ||
      payload.role === "fighter" ||
      payload.role === "management" ||
      payload.role === "admin"
    ) {
      return payload.role;
    }
  } catch {
    return null;
  }
  return null;
}

function base64UrlDecode(value: string): string {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padding = normalized.length % 4;
  const padded = padding === 0 ? normalized : normalized + "=".repeat(4 - padding);
  return atob(padded);
}

export function createIdempotencyKey(prefix: string): string {
  const randomPart = Math.random().toString(36).slice(2, 10);
  return `${prefix}-${Date.now()}-${randomPart}`;
}

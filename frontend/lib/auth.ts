/** Client-side JWT storage. Only ever touched in the browser (all callers
 * guard on `typeof window !== "undefined"` before importing/using this from
 * a Server Component context, but the functions no-op safely either way). */
const TOKEN_KEY = "internship_pipeline_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}

export function isLoggedIn(): boolean {
  return getToken() !== null;
}

import { getToken } from "@/lib/auth";

export class FetchError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "FetchError";
  }
}

export async function fetcher<T = unknown>(url: string): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(url, { headers });

  if (!res.ok) {
    throw new FetchError(
      `API request failed: ${res.status} ${res.statusText}`,
      res.status
    );
  }

  const text = await res.text();
  if (!text) return undefined as T;
  return JSON.parse(text) as T;
}

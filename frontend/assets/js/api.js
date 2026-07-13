// The single place in the app that calls fetch(). Every page/module talks to
// the backend through apiRequest() so headers, base URL, and error handling
// live in exactly one place.
import { API_BASE_URL } from "./config.js";
import { getToken, logout } from "./auth.js";

// Distinct from a plain Error so callers (guard.js in particular) can tell
// "the server is unreachable" apart from "the server said no" - a network
// blip shouldn't be treated the same as an invalid session.
export class NetworkError extends Error {}

export async function apiRequest(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new NetworkError("Could not reach the server. Is the API running?");
  }

  // Only treat a 401 as "your session died" when a token was actually sent.
  // An anonymous request (e.g. POST /auth/login with the wrong password)
  // getting a 401 is just a normal rejected request, not a stale session -
  // it falls through to the generic error handling below so the caller
  // (e.g. login.js) can show its own message instead of being redirected.
  if (res.status === 401 && token) {
    logout();
    throw new Error("Session expired. Please log in again.");
  }

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed (${res.status})`);
  }

  return res.status === 204 ? null : res.json();
}

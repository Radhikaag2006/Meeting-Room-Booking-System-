// Runs at the top of every protected page. Confirms the token is valid
// server-side (not just present) and that the caller holds the role the
// page requires, mirroring the backend's own per-router role check so the
// UI never shows a screen the API would 403 on.
import { apiRequest, NetworkError } from "./api.js";
import { getToken, clearToken } from "./auth.js";

export async function requireRole(requiredRole) {
  const token = getToken();
  if (!token) {
    window.location.href = "/index.html";
    return null;
  }

  let user;
  try {
    user = await apiRequest("/auth/me");
  } catch (err) {
    // A network outage doesn't mean the session is invalid - don't clear
    // the token or bounce a legitimately logged-in user back to login just
    // because the server is temporarily unreachable.
    if (err instanceof NetworkError) {
      renderConnectionError(requiredRole);
    } else {
      clearToken();
      window.location.href = "/index.html";
    }
    return null;
  }

  if (user.role !== requiredRole) {
    clearToken();
    window.location.href = "/index.html";
    return null;
  }

  return user;
}

function renderConnectionError() {
  document.body.innerHTML = `
    <div class="page-error-shell">
      <div class="empty-state is-error">
        <p>Could not reach the server. Your session is still active - check your connection and try again.</p>
        <button type="button" class="btn btn-secondary" id="guard-retry-btn">Retry</button>
      </div>
    </div>
  `;
  document.getElementById("guard-retry-btn").addEventListener("click", () => window.location.reload());
}

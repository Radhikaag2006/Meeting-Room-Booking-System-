// Token storage + role helpers. sessionStorage is used deliberately so a
// closed tab always requires a fresh login rather than keeping stale tokens alive.
const TOKEN_KEY = "mrbs_token";

export function setToken(token) {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
}

export function isLoggedIn() {
  return Boolean(getToken());
}

// Decodes the JWT payload client-side for immediate UI decisions (e.g. which
// dashboard to redirect to). This is NOT a trust boundary - guard.js confirms
// the token server-side via GET /auth/me before rendering any protected page.
function decodePayload(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
        .join("")
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function getRole() {
  const token = getToken();
  if (!token) return null;
  const payload = decodePayload(token);
  return payload ? payload.role : null;
}

export function dashboardPathForRole(role) {
  switch (role) {
    case "SUPER_ADMIN":
      return "/super-admin/dashboard.html";
    case "OFFICE_ADMIN":
      return "/office-admin/dashboard.html";
    case "EMPLOYEE":
      return "/employee/dashboard.html";
    default:
      return "/index.html";
  }
}

// Paths are root-relative (e.g. "/index.html"): the whole frontend/ folder
// is served as one static site root (see README), so this works from any page.
export function logout() {
  clearToken();
  window.location.href = "/index.html";
}

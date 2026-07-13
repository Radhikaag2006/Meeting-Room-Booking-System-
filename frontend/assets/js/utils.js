// Escapes user-generated text before it's interpolated into innerHTML
// (office names, employee names, emails, etc. all come from other users'
// input and get rendered back into tables/forms).
export function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[ch]);
}

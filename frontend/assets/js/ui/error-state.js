import { escapeHtml } from "../utils.js";

// Replaces a container's contents (skeleton, table, whatever) with a
// persistent error message + retry button. Used when the *initial* load of
// a page's primary data fails, so the UI doesn't sit on a loading skeleton
// forever after a toast has already faded out.
export function renderErrorState(container, message, onRetry) {
  container.innerHTML = `
    <div class="empty-state is-error">
      <p>${escapeHtml(message)}</p>
      <button type="button" class="btn btn-secondary" id="retry-btn">Retry</button>
    </div>
  `;
  container.querySelector("#retry-btn").addEventListener("click", onRetry);
}

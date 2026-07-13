// Fixed-position success/error notifications. Lazily creates its own
// container so any page can call showToast() without extra markup.
function getContainer() {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  return container;
}

export function showToast(message, type = "success", duration = 3500) {
  const container = getContainer();
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, duration);
}

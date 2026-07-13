import { escapeHtml } from "../utils.js";

// Reusable confirm dialog, used for every delete/cancel action so no page
// has to hand-roll a confirmation flow.
export function confirmModal({ title, message, confirmLabel = "Confirm", danger = true }) {
  return new Promise((resolve) => {
    const backdrop = document.createElement("div");
    backdrop.className = "modal-backdrop";
    // title/message often embed a user-supplied name (office name, meeting
    // title, ...) - escape so that can never be interpreted as markup.
    backdrop.innerHTML = `
      <div class="modal" role="dialog" aria-modal="true">
        <h3>${escapeHtml(title)}</h3>
        <p>${escapeHtml(message)}</p>
        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" data-action="cancel">Cancel</button>
          <button type="button" class="btn ${danger ? "btn-danger" : "btn-primary"}" data-action="confirm">${escapeHtml(confirmLabel)}</button>
        </div>
      </div>
    `;

    function close(result) {
      document.removeEventListener("keydown", onKeydown);
      backdrop.remove();
      resolve(result);
    }

    function onKeydown(e) {
      if (e.key === "Escape") close(false);
    }

    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) close(false);
    });
    backdrop.querySelector('[data-action="cancel"]').addEventListener("click", () => close(false));
    backdrop.querySelector('[data-action="confirm"]').addEventListener("click", () => close(true));
    document.addEventListener("keydown", onKeydown);

    document.body.appendChild(backdrop);
    backdrop.querySelector('[data-action="cancel"]').focus();
  });
}

// Generic form-in-modal for create/edit flows, shared by every admin CRUD
// screen. fields: [{ name, label, type: "text"|"email"|"password"|"select",
// required, options: [{ value, label }] (for "select") }]
// Resolves with a { [field.name]: value } object on submit, or null on cancel.
export function formModal({ title, fields, initialValues = {}, submitLabel = "Save" }) {
  return new Promise((resolve) => {
    const backdrop = document.createElement("div");
    backdrop.className = "modal-backdrop";
    backdrop.innerHTML = `
      <div class="modal" role="dialog" aria-modal="true">
        <h3>${escapeHtml(title)}</h3>
        <form novalidate>
          ${fields.map((f) => fieldHtml(f, initialValues[f.name])).join("")}
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" data-action="cancel">Cancel</button>
            <button type="submit" class="btn btn-primary">${escapeHtml(submitLabel)}</button>
          </div>
        </form>
      </div>
    `;

    function close(result) {
      document.removeEventListener("keydown", onKeydown);
      backdrop.remove();
      resolve(result);
    }

    function onKeydown(e) {
      if (e.key === "Escape") close(null);
    }

    const form = backdrop.querySelector("form");

    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) close(null);
    });
    backdrop.querySelector('[data-action="cancel"]').addEventListener("click", () => close(null));
    document.addEventListener("keydown", onKeydown);

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const values = {};
      for (const f of fields) {
        values[f.name] = form.elements[f.name].value;
      }
      close(values);
    });

    document.body.appendChild(backdrop);
    form.querySelector("input, select, textarea")?.focus();
  });
}

function fieldHtml(field, value = "") {
  const requiredAttr = field.required === false ? "" : "required";
  const id = `field-${field.name}`;

  if (field.type === "select") {
    const options = field.options
      .map(
        (opt) =>
          `<option value="${escapeHtml(opt.value)}" ${String(opt.value) === String(value) ? "selected" : ""}>${escapeHtml(opt.label)}</option>`
      )
      .join("");
    return `
      <div class="field">
        <label for="${id}">${escapeHtml(field.label)}</label>
        <select id="${id}" name="${field.name}" ${requiredAttr}>${options}</select>
      </div>
    `;
  }

  if (field.type === "textarea") {
    return `
      <div class="field">
        <label for="${id}">${escapeHtml(field.label)}</label>
        <textarea id="${id}" name="${field.name}" ${requiredAttr}>${escapeHtml(value)}</textarea>
      </div>
    `;
  }

  const minAttr = field.min !== undefined ? `min="${field.min}"` : "";
  return `
    <div class="field">
      <label for="${id}">${escapeHtml(field.label)}</label>
      <input id="${id}" name="${field.name}" type="${field.type || "text"}" value="${escapeHtml(value)}" ${requiredAttr} ${minAttr} />
    </div>
  `;
}

import { requireRole } from "../../guard.js";
import { initLayout } from "../../layout.js";
import { apiRequest } from "../../api.js";
import { renderTable } from "../../ui/table.js";
import { formModal, confirmModal } from "../../ui/modal.js";
import { showToast } from "../../ui/toast.js";
import { renderErrorState } from "../../ui/error-state.js";
import { escapeHtml } from "../../utils.js";

const OFFICE_FIELDS = [
  { name: "office_name", label: "Office Name" },
  { name: "address", label: "Address" },
  { name: "city", label: "City" },
  { name: "state", label: "State" },
  { name: "country", label: "Country" },
];

const tableContainer = document.getElementById("table-container");

async function loadOffices() {
  const offices = await apiRequest("/offices/");
  renderTable(tableContainer, {
    columns: [
      { label: "Office Name", render: (o) => escapeHtml(o.office_name) },
      { label: "City", render: (o) => escapeHtml(o.city) },
      { label: "State", render: (o) => escapeHtml(o.state) },
      { label: "Country", render: (o) => escapeHtml(o.country) },
      { label: "Address", render: (o) => escapeHtml(o.address) },
      {
        label: "",
        render: (o) => `
          <div class="row-actions">
            <button type="button" class="btn btn-secondary" data-action="edit" data-id="${o.office_id}">Edit</button>
            <button type="button" class="btn btn-danger" data-action="delete" data-id="${o.office_id}">Delete</button>
          </div>
        `,
      },
    ],
    rows: offices,
    emptyMessage: "No offices yet. Create the first one to get started.",
  });

  tableContainer.querySelectorAll('[data-action="edit"]').forEach((btn) => {
    btn.addEventListener("click", () => editOffice(Number(btn.dataset.id), offices));
  });
  tableContainer.querySelectorAll('[data-action="delete"]').forEach((btn) => {
    btn.addEventListener("click", () => deleteOffice(Number(btn.dataset.id), offices));
  });
}

async function createOffice() {
  const values = await formModal({ title: "New Office", fields: OFFICE_FIELDS, submitLabel: "Create" });
  if (!values) return;
  try {
    await apiRequest("/offices/", { method: "POST", body: values });
    showToast("Office created", "success");
    await loadOffices();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function editOffice(officeId, offices) {
  const office = offices.find((o) => o.office_id === officeId);
  const values = await formModal({
    title: "Edit Office",
    fields: OFFICE_FIELDS,
    initialValues: office,
    submitLabel: "Save",
  });
  if (!values) return;
  try {
    await apiRequest(`/offices/${officeId}`, { method: "PUT", body: values });
    showToast("Office updated", "success");
    await loadOffices();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteOffice(officeId, offices) {
  const office = offices.find((o) => o.office_id === officeId);
  const confirmed = await confirmModal({
    title: "Delete office",
    message: `Delete "${office.office_name}"? This cannot be undone.`,
    confirmLabel: "Delete",
  });
  if (!confirmed) return;
  try {
    await apiRequest(`/offices/${officeId}`, { method: "DELETE" });
    showToast("Office deleted", "success");
    await loadOffices();
  } catch (err) {
    showToast(err.message, "error");
  }
}

const user = await requireRole("SUPER_ADMIN");
if (user) {
  initLayout({ role: "SUPER_ADMIN", user });
  document.getElementById("new-office-btn").addEventListener("click", createOffice);
  try {
    await loadOffices();
  } catch (err) {
    showToast(err.message, "error");
    renderErrorState(tableContainer, "Couldn't load offices.", loadOffices);
  }
}

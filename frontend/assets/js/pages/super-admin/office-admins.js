import { requireRole } from "../../guard.js";
import { initLayout } from "../../layout.js";
import { apiRequest } from "../../api.js";
import { renderTable } from "../../ui/table.js";
import { formModal, confirmModal } from "../../ui/modal.js";
import { showToast } from "../../ui/toast.js";
import { renderErrorState } from "../../ui/error-state.js";
import { escapeHtml } from "../../utils.js";

const STATUS_OPTIONS = [
  { value: "ACTIVE", label: "Active" },
  { value: "INACTIVE", label: "Inactive" },
];

const tableContainer = document.getElementById("table-container");
let officesById = new Map();

async function loadOfficeOptions() {
  const offices = await apiRequest("/offices/");
  officesById = new Map(offices.map((o) => [o.office_id, o]));
  return offices.map((o) => ({ value: o.office_id, label: o.office_name }));
}

function officeName(officeId) {
  const office = officesById.get(officeId);
  return office ? escapeHtml(office.office_name) : `#${officeId}`;
}

async function loadOfficeAdmins() {
  const [admins] = await Promise.all([apiRequest("/office-admins"), loadOfficeOptions()]);

  renderTable(tableContainer, {
    columns: [
      { label: "Name", render: (a) => escapeHtml(`${a.first_name} ${a.last_name}`) },
      { label: "Email", render: (a) => escapeHtml(a.email) },
      { label: "Office", render: (a) => officeName(a.office_id) },
      {
        label: "Status",
        render: (a) =>
          a.status === "ACTIVE"
            ? '<span class="badge badge-success">Active</span>'
            : '<span class="badge badge-neutral">Inactive</span>',
      },
      {
        label: "",
        render: (a) => `
          <div class="row-actions">
            <button type="button" class="btn btn-secondary" data-action="edit" data-id="${a.user_id}">Edit</button>
            <button type="button" class="btn btn-danger" data-action="delete" data-id="${a.user_id}">Delete</button>
          </div>
        `,
      },
    ],
    rows: admins,
    emptyMessage: "No office admins yet. Create the first one to get started.",
  });

  tableContainer.querySelectorAll('[data-action="edit"]').forEach((btn) => {
    btn.addEventListener("click", () => editOfficeAdmin(Number(btn.dataset.id), admins));
  });
  tableContainer.querySelectorAll('[data-action="delete"]').forEach((btn) => {
    btn.addEventListener("click", () => deleteOfficeAdmin(Number(btn.dataset.id), admins));
  });
}

async function createOfficeAdmin() {
  const officeOptions = Array.from(officesById.values()).map((o) => ({ value: o.office_id, label: o.office_name }));
  if (officeOptions.length === 0) {
    showToast("Create an office first — an office admin must belong to one.", "error");
    return;
  }

  const values = await formModal({
    title: "New Office Admin",
    fields: [
      { name: "first_name", label: "First Name" },
      { name: "last_name", label: "Last Name" },
      { name: "email", label: "Email", type: "email" },
      { name: "password", label: "Password", type: "password" },
      { name: "office_id", label: "Office", type: "select", options: officeOptions },
    ],
    submitLabel: "Create",
  });
  if (!values) return;

  try {
    await apiRequest("/office-admins", {
      method: "POST",
      body: { ...values, office_id: Number(values.office_id) },
    });
    showToast("Office admin created", "success");
    await loadOfficeAdmins();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function editOfficeAdmin(userId, admins) {
  const admin = admins.find((a) => a.user_id === userId);
  const values = await formModal({
    title: "Edit Office Admin",
    fields: [
      { name: "first_name", label: "First Name" },
      { name: "last_name", label: "Last Name" },
      { name: "email", label: "Email", type: "email" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
    initialValues: admin,
    submitLabel: "Save",
  });
  if (!values) return;

  try {
    await apiRequest(`/office-admins/${userId}`, { method: "PUT", body: values });
    showToast("Office admin updated", "success");
    await loadOfficeAdmins();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteOfficeAdmin(userId, admins) {
  const admin = admins.find((a) => a.user_id === userId);
  const confirmed = await confirmModal({
    title: "Delete office admin",
    message: `Delete "${admin.first_name} ${admin.last_name}"? This cannot be undone.`,
    confirmLabel: "Delete",
  });
  if (!confirmed) return;

  try {
    await apiRequest(`/office-admins/${userId}`, { method: "DELETE" });
    showToast("Office admin deleted", "success");
    await loadOfficeAdmins();
  } catch (err) {
    showToast(err.message, "error");
  }
}

const user = await requireRole("SUPER_ADMIN");
if (user) {
  initLayout({ role: "SUPER_ADMIN", user });
  document.getElementById("new-admin-btn").addEventListener("click", createOfficeAdmin);
  try {
    await loadOfficeAdmins();
  } catch (err) {
    showToast(err.message, "error");
    renderErrorState(tableContainer, "Couldn't load office admins.", loadOfficeAdmins);
  }
}

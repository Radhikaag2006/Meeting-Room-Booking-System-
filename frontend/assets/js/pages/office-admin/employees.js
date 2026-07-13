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

async function loadEmployees() {
  const employees = await apiRequest("/employees");
  renderTable(tableContainer, {
    columns: [
      { label: "Name", render: (e) => escapeHtml(`${e.first_name} ${e.last_name}`) },
      { label: "Email", render: (e) => escapeHtml(e.email) },
      {
        label: "Status",
        render: (e) =>
          e.status === "ACTIVE"
            ? '<span class="badge badge-success">Active</span>'
            : '<span class="badge badge-neutral">Inactive</span>',
      },
      {
        label: "",
        render: (e) => `
          <div class="row-actions">
            <button type="button" class="btn btn-secondary" data-action="edit" data-id="${e.user_id}">Edit</button>
            <button type="button" class="btn btn-danger" data-action="delete" data-id="${e.user_id}">Delete</button>
          </div>
        `,
      },
    ],
    rows: employees,
    emptyMessage: "No employees yet. Create the first one to get started.",
  });

  tableContainer.querySelectorAll('[data-action="edit"]').forEach((btn) => {
    btn.addEventListener("click", () => editEmployee(Number(btn.dataset.id), employees));
  });
  tableContainer.querySelectorAll('[data-action="delete"]').forEach((btn) => {
    btn.addEventListener("click", () => deleteEmployee(Number(btn.dataset.id), employees));
  });
}

async function createEmployee() {
  const values = await formModal({
    title: "New Employee",
    fields: [
      { name: "first_name", label: "First Name" },
      { name: "last_name", label: "Last Name" },
      { name: "email", label: "Email", type: "email" },
      { name: "password", label: "Password", type: "password" },
    ],
    submitLabel: "Create",
  });
  if (!values) return;

  try {
    await apiRequest("/employees", { method: "POST", body: values });
    showToast("Employee created", "success");
    await loadEmployees();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function editEmployee(userId, employees) {
  const employee = employees.find((e) => e.user_id === userId);
  const values = await formModal({
    title: "Edit Employee",
    fields: [
      { name: "first_name", label: "First Name" },
      { name: "last_name", label: "Last Name" },
      { name: "email", label: "Email", type: "email" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
    initialValues: employee,
    submitLabel: "Save",
  });
  if (!values) return;

  try {
    await apiRequest(`/employees/${userId}`, { method: "PUT", body: values });
    showToast("Employee updated", "success");
    await loadEmployees();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteEmployee(userId, employees) {
  const employee = employees.find((e) => e.user_id === userId);
  const confirmed = await confirmModal({
    title: "Delete employee",
    message: `Delete "${employee.first_name} ${employee.last_name}"? This cannot be undone.`,
    confirmLabel: "Delete",
  });
  if (!confirmed) return;

  try {
    await apiRequest(`/employees/${userId}`, { method: "DELETE" });
    showToast("Employee deleted", "success");
    await loadEmployees();
  } catch (err) {
    showToast(err.message, "error");
  }
}

const user = await requireRole("OFFICE_ADMIN");
if (user) {
  initLayout({ role: "OFFICE_ADMIN", user });
  document.getElementById("new-employee-btn").addEventListener("click", createEmployee);
  try {
    await loadEmployees();
  } catch (err) {
    showToast(err.message, "error");
    renderErrorState(tableContainer, "Couldn't load employees.", loadEmployees);
  }
}

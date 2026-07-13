import { requireRole } from "../../guard.js";
import { initLayout } from "../../layout.js";
import { apiRequest } from "../../api.js";
import { showToast } from "../../ui/toast.js";
import { renderErrorState } from "../../ui/error-state.js";

const content = document.getElementById("page-content");
let user;

async function loadDashboard() {
  content.innerHTML = `<div class="card">Welcome, ${user.first_name} ${user.last_name}</div>`;

  try {
    const [employees, rooms] = await Promise.all([
      apiRequest("/employees"),
      apiRequest("/meeting-rooms"),
    ]);

    content.innerHTML = `
      <div class="stats-grid">
        <div class="card stat-card">
          <div class="stat-value">${employees.length}</div>
          <div class="stat-label">Employees</div>
          <a href="/office-admin/employees.html">Manage employees &rarr;</a>
        </div>
        <div class="card stat-card">
          <div class="stat-value">${rooms.length}</div>
          <div class="stat-label">Meeting Rooms</div>
          <a href="/office-admin/meeting-rooms.html">Manage meeting rooms &rarr;</a>
        </div>
      </div>
    `;
  } catch (err) {
    showToast(err.message, "error");
    renderErrorState(content, "Couldn't load dashboard data.", loadDashboard);
  }
}

user = await requireRole("OFFICE_ADMIN");
if (user) {
  initLayout({ role: "OFFICE_ADMIN", user });
  await loadDashboard();
}

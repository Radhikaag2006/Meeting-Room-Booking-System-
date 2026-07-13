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
    const [offices, admins] = await Promise.all([
      apiRequest("/offices/"),
      apiRequest("/office-admins"),
    ]);

    content.innerHTML = `
      <div class="stats-grid">
        <div class="card stat-card">
          <div class="stat-value">${offices.length}</div>
          <div class="stat-label">Offices</div>
          <a href="/super-admin/offices.html">Manage offices &rarr;</a>
        </div>
        <div class="card stat-card">
          <div class="stat-value">${admins.length}</div>
          <div class="stat-label">Office Admins</div>
          <a href="/super-admin/office-admins.html">Manage office admins &rarr;</a>
        </div>
      </div>
    `;
  } catch (err) {
    showToast(err.message, "error");
    renderErrorState(content, "Couldn't load dashboard data.", loadDashboard);
  }
}

user = await requireRole("SUPER_ADMIN");
if (user) {
  initLayout({ role: "SUPER_ADMIN", user });
  await loadDashboard();
}

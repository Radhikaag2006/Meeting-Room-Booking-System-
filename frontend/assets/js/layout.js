// Injects the shared sidebar/topbar chrome into every protected page.
// Pages provide an empty <aside id="sidebar"> and <header id="topbar">
// shell in their HTML; this fills them in based on the logged-in role.
import { logout } from "./auth.js";

const NAV_ITEMS = {
  SUPER_ADMIN: [
    { label: "Dashboard", href: "/super-admin/dashboard.html" },
    { label: "Offices", href: "/super-admin/offices.html" },
    { label: "Office Admins", href: "/super-admin/office-admins.html" },
  ],
  OFFICE_ADMIN: [
    { label: "Dashboard", href: "/office-admin/dashboard.html" },
    { label: "Employees", href: "/office-admin/employees.html" },
    { label: "Meeting Rooms", href: "/office-admin/meeting-rooms.html" },
  ],
  EMPLOYEE: [
    { label: "Dashboard", href: "/employee/dashboard.html" },
    { label: "New Booking", href: "/employee/new-booking.html" },
    { label: "My Meetings", href: "/employee/my-meetings.html" },
  ],
};

const ROLE_LABELS = {
  SUPER_ADMIN: "Super Admin",
  OFFICE_ADMIN: "Office Admin",
  EMPLOYEE: "Employee",
};

export function initLayout({ role, user }) {
  const sidebar = document.getElementById("sidebar");
  const topbar = document.getElementById("topbar");
  if (!sidebar || !topbar) return;

  sidebar.dataset.role = role;
  const currentPath = window.location.pathname;
  const navLinks = (NAV_ITEMS[role] || [])
    .map(
      (item) =>
        `<a href="${item.href}" class="${currentPath === item.href ? "active" : ""}">${item.label}</a>`
    )
    .join("");

  sidebar.innerHTML = `
    <div class="brand">MRBS</div>
    <div class="role-label">${ROLE_LABELS[role] || role}</div>
    <nav>${navLinks}</nav>
    <div class="sidebar-footer">
      <button type="button" class="btn btn-secondary btn-block" id="logout-btn">Log out</button>
    </div>
  `;

  topbar.innerHTML = `
    <button type="button" class="btn btn-icon hamburger" id="hamburger-btn" aria-label="Toggle menu">&#9776;</button>
    <div class="user-info">${user ? `${user.first_name} ${user.last_name}` : ""}</div>
  `;

  let backdrop = document.querySelector(".sidebar-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.className = "sidebar-backdrop";
    document.body.appendChild(backdrop);
  }

  function toggleSidebar(open) {
    sidebar.classList.toggle("open", open);
    backdrop.classList.toggle("open", open);
  }

  document.getElementById("logout-btn").addEventListener("click", logout);
  document.getElementById("hamburger-btn").addEventListener("click", () => {
    toggleSidebar(!sidebar.classList.contains("open"));
  });
  backdrop.addEventListener("click", () => toggleSidebar(false));
  sidebar.querySelectorAll("nav a").forEach((link) => link.addEventListener("click", () => toggleSidebar(false)));
}

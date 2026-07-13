import { requireRole } from "../../guard.js";
import { initLayout } from "../../layout.js";
import { apiRequest } from "../../api.js";
import { showToast } from "../../ui/toast.js";
import { renderErrorState } from "../../ui/error-state.js";
import { escapeHtml } from "../../utils.js";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

const content = document.getElementById("page-content");
let user;

async function loadDashboard() {
  content.innerHTML = `<div class="card">Welcome, ${user.first_name} ${user.last_name}</div>`;

  try {
    const bookings = await apiRequest("/bookings/my-meetings");
    const today = todayIso();
    const upcoming = bookings
      .filter((b) => b.status === "SCHEDULED" && b.meeting_date >= today)
      .sort((a, b) => (a.meeting_date + a.start_time).localeCompare(b.meeting_date + b.start_time));

    const upcomingRows = upcoming
      .slice(0, 5)
      .map(
        (b) => `
          <li>
            <a href="/employee/booking-detail.html?id=${b.booking_id}">${escapeHtml(b.meeting_title)}</a>
            <span class="stat-label">${escapeHtml(b.meeting_date)} &middot; ${escapeHtml(b.start_time)}&ndash;${escapeHtml(b.end_time)}</span>
          </li>
        `
      )
      .join("");

    content.innerHTML = `
      <div class="stats-grid">
        <div class="card stat-card">
          <div class="stat-value">${upcoming.length}</div>
          <div class="stat-label">Upcoming Meetings</div>
          <a href="/employee/my-meetings.html">View all meetings &rarr;</a>
        </div>
        <div class="card stat-card">
          <a href="/employee/new-booking.html" class="btn btn-primary btn-block">New Booking</a>
        </div>
      </div>
      <div class="card">
        <h3>Next up</h3>
        <ul>${upcomingRows || '<li class="empty-state">No upcoming meetings.</li>'}</ul>
      </div>
    `;
  } catch (err) {
    showToast(err.message, "error");
    renderErrorState(content, "Couldn't load your meetings.", loadDashboard);
  }
}

user = await requireRole("EMPLOYEE");
if (user) {
  initLayout({ role: "EMPLOYEE", user });
  await loadDashboard();
}

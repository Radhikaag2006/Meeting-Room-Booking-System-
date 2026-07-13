import { requireRole } from "../../guard.js";
import { initLayout } from "../../layout.js";
import { apiRequest } from "../../api.js";
import { renderTable } from "../../ui/table.js";
import { showToast } from "../../ui/toast.js";
import { renderErrorState } from "../../ui/error-state.js";
import { escapeHtml } from "../../utils.js";

const STATUS_BADGES = {
  SCHEDULED: '<span class="badge badge-success">Scheduled</span>',
  CANCELLED: '<span class="badge badge-danger">Cancelled</span>',
  COMPLETED: '<span class="badge badge-neutral">Completed</span>',
};

const tableContainer = document.getElementById("table-container");

async function loadMeetings() {
  const [bookings, rooms] = await Promise.all([
    apiRequest("/bookings/my-meetings"),
    apiRequest("/meeting-rooms/available"),
  ]);
  const roomsById = new Map(rooms.map((r) => [r.room_id, r]));

  const sorted = [...bookings].sort((a, b) =>
    (b.meeting_date + b.start_time).localeCompare(a.meeting_date + a.start_time)
  );

  renderTable(tableContainer, {
    columns: [
      { label: "Title", render: (b) => escapeHtml(b.meeting_title) },
      { label: "Date", render: (b) => escapeHtml(b.meeting_date) },
      { label: "Time", render: (b) => `${escapeHtml(b.start_time)}–${escapeHtml(b.end_time)}` },
      {
        label: "Room",
        render: (b) => escapeHtml(roomsById.get(b.room_id)?.room_name ?? `#${b.room_id}`),
      },
      { label: "Status", render: (b) => STATUS_BADGES[b.status] ?? escapeHtml(b.status) },
      {
        label: "",
        render: (b) => `<a class="btn btn-secondary" href="/employee/booking-detail.html?id=${b.booking_id}">View</a>`,
      },
    ],
    rows: sorted,
    emptyMessage: "No meetings yet. Create your first booking.",
  });
}

const user = await requireRole("EMPLOYEE");
if (user) {
  initLayout({ role: "EMPLOYEE", user });
  try {
    await loadMeetings();
  } catch (err) {
    showToast(err.message, "error");
    renderErrorState(tableContainer, "Couldn't load your meetings.", loadMeetings);
  }
}

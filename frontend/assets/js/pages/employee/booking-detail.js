import { requireRole } from "../../guard.js";
import { initLayout } from "../../layout.js";
import { apiRequest } from "../../api.js";
import { formModal, confirmModal } from "../../ui/modal.js";
import { showToast } from "../../ui/toast.js";
import { renderErrorState } from "../../ui/error-state.js";
import { escapeHtml } from "../../utils.js";
import { endAfterStart, validateForm } from "../../validators.js";

const STATUS_BADGES = {
  SCHEDULED: '<span class="badge badge-success">Scheduled</span>',
  CANCELLED: '<span class="badge badge-danger">Cancelled</span>',
  COMPLETED: '<span class="badge badge-neutral">Completed</span>',
};

const bookingId = new URLSearchParams(window.location.search).get("id");
const container = document.getElementById("detail-container");

let currentUser;
let rooms = [];
let colleagues = [];

function roomOptions() {
  return rooms.map((r) => ({ value: r.room_id, label: `${r.room_name} (capacity ${r.capacity})` }));
}

function organizerLabel(booking) {
  if (booking.organizer_id === currentUser.user_id) return "You";
  const colleague = colleagues.find((c) => c.user_id === booking.organizer_id);
  return colleague ? `${colleague.first_name} ${colleague.last_name}` : `Employee #${booking.organizer_id}`;
}

function roomLabel(booking) {
  const room = rooms.find((r) => r.room_id === booking.room_id);
  return room ? room.room_name : `#${booking.room_id}`;
}

async function loadBooking() {
  const booking = await apiRequest(`/bookings/${bookingId}`);
  const isOrganizer = booking.organizer_id === currentUser.user_id;

  container.innerHTML = `
    <div class="card">
      <div class="page-header">
        <h3>${escapeHtml(booking.meeting_title)}</h3>
        ${STATUS_BADGES[booking.status] ?? escapeHtml(booking.status)}
      </div>
      <dl class="detail-grid">
        <dt>Description</dt><dd>${booking.description ? escapeHtml(booking.description) : "&mdash;"}</dd>
        <dt>Room</dt><dd>${escapeHtml(roomLabel(booking))}</dd>
        <dt>Date</dt><dd>${escapeHtml(booking.meeting_date)}</dd>
        <dt>Time</dt><dd>${escapeHtml(booking.start_time)}&ndash;${escapeHtml(booking.end_time)}</dd>
        <dt>Organizer</dt><dd>${escapeHtml(organizerLabel(booking))}</dd>
      </dl>
      ${
        isOrganizer
          ? `
            <div class="row-actions">
              <button type="button" class="btn btn-secondary" id="edit-btn">Edit</button>
              ${booking.status === "SCHEDULED" ? '<button type="button" class="btn btn-danger" id="cancel-btn">Cancel Meeting</button>' : ""}
            </div>
          `
          : '<p class="stat-label">You were invited to this meeting; only the organizer can edit or cancel it.</p>'
      }
    </div>
  `;

  if (isOrganizer) {
    document.getElementById("edit-btn").addEventListener("click", () => editBooking(booking));
    const cancelBtn = document.getElementById("cancel-btn");
    if (cancelBtn) cancelBtn.addEventListener("click", () => cancelBooking(booking));
  }
}

async function editBooking(booking) {
  const values = await formModal({
    title: "Edit Booking",
    fields: [
      { name: "meeting_title", label: "Meeting Title" },
      { name: "description", label: "Description", type: "textarea", required: false },
      { name: "room_id", label: "Room", type: "select", options: roomOptions() },
      { name: "meeting_date", label: "Date", type: "date", min: new Date().toISOString().slice(0, 10) },
      { name: "start_time", label: "Start Time", type: "time" },
      { name: "end_time", label: "End Time", type: "time" },
    ],
    initialValues: booking,
    submitLabel: "Save",
  });
  if (!values) return;

  const timeError = endAfterStart(values.start_time, values.end_time);
  if (timeError) {
    showToast(timeError, "error");
    return;
  }

  try {
    await apiRequest(`/bookings/${bookingId}`, {
      method: "PUT",
      body: { ...values, room_id: Number(values.room_id), description: values.description || null },
    });
    showToast("Booking updated", "success");
    await loadBooking();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function cancelBooking(booking) {
  const confirmed = await confirmModal({
    title: "Cancel meeting",
    message: `Cancel "${booking.meeting_title}"? Attendees will no longer see it as scheduled.`,
    confirmLabel: "Cancel Meeting",
  });
  if (!confirmed) return;

  try {
    await apiRequest(`/bookings/${bookingId}/cancel`, { method: "PATCH" });
    showToast("Meeting cancelled", "success");
    await loadBooking();
  } catch (err) {
    showToast(err.message, "error");
  }
}

currentUser = await requireRole("EMPLOYEE");
if (currentUser) {
  initLayout({ role: "EMPLOYEE", user: currentUser });

  if (!bookingId) {
    container.innerHTML = '<div class="empty-state">No booking specified.</div>';
  } else {
    await loadAll();
  }
}

async function loadAll() {
  try {
    [rooms, colleagues] = await Promise.all([
      apiRequest("/meeting-rooms/available"),
      apiRequest("/employees/colleagues"),
    ]);
    await loadBooking();
  } catch (err) {
    showToast(err.message, "error");
    renderErrorState(container, "Couldn't load this booking.", loadAll);
  }
}

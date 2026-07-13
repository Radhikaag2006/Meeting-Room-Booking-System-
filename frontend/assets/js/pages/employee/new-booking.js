import { requireRole } from "../../guard.js";
import { initLayout } from "../../layout.js";
import { apiRequest } from "../../api.js";
import { showToast } from "../../ui/toast.js";
import { renderErrorState } from "../../ui/error-state.js";
import { escapeHtml } from "../../utils.js";
import { endAfterStart, validateForm } from "../../validators.js";

const formContainer = document.getElementById("form-container");
const form = document.getElementById("booking-form");
const roomSelect = document.getElementById("room_id");
const attendeesList = document.getElementById("attendees-list");
const dateInput = document.getElementById("meeting_date");
const startInput = document.getElementById("start_time");
const endInput = document.getElementById("end_time");
const submitBtn = document.getElementById("submit-btn");

async function loadFormOptions() {
  const [rooms, colleagues] = await Promise.all([
    apiRequest("/meeting-rooms/available"),
    apiRequest("/employees/colleagues"),
  ]);

  roomSelect.innerHTML = rooms.length
    ? rooms
        .map((r) => `<option value="${r.room_id}">${escapeHtml(r.room_name)} (capacity ${r.capacity})</option>`)
        .join("")
    : `<option value="" disabled selected>No bookable rooms in your office</option>`;

  attendeesList.innerHTML = colleagues.length
    ? colleagues
        .map(
          (c) => `
            <div class="checkbox-item">
              <input type="checkbox" id="attendee-${c.user_id}" name="attendees" value="${c.user_id}" />
              <label for="attendee-${c.user_id}">${escapeHtml(`${c.first_name} ${c.last_name}`)} &lt;${escapeHtml(c.email)}&gt;</label>
            </div>
          `
        )
        .join("")
    : `<div class="empty-state">No other active employees in your office to invite.</div>`;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const isValid = validateForm([[endInput, [(v) => endAfterStart(startInput.value, v)]]]);
  if (!form.reportValidity() || !isValid) return;

  const attendees = Array.from(attendeesList.querySelectorAll('input[name="attendees"]:checked')).map((el) =>
    Number(el.value)
  );

  submitBtn.disabled = true;
  submitBtn.textContent = "Creating…";

  try {
    await apiRequest("/bookings", {
      method: "POST",
      body: {
        meeting_title: form.elements.meeting_title.value,
        description: form.elements.description.value || null,
        room_id: Number(roomSelect.value),
        meeting_date: dateInput.value,
        start_time: startInput.value,
        end_time: endInput.value,
        attendees,
      },
    });
    showToast("Booking created", "success");
    window.location.href = "/employee/my-meetings.html";
  } catch (err) {
    showToast(err.message, "error");
    submitBtn.disabled = false;
    submitBtn.textContent = "Create Booking";
  }
});

const user = await requireRole("EMPLOYEE");
if (user) {
  initLayout({ role: "EMPLOYEE", user });
  dateInput.min = new Date().toISOString().slice(0, 10);
  try {
    await loadFormOptions();
  } catch (err) {
    showToast(err.message, "error");
    // loadFormOptions only fills the room/attendee selects, not the whole
    // form - a full reload is the simplest correct "retry" once it's failed.
    renderErrorState(formContainer, "Couldn't load the booking form.", () => window.location.reload());
  }
}
